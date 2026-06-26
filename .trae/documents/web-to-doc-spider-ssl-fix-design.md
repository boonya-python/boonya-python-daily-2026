# Web-to-Doc Spider SSL 错误修复设计

## 一、问题分析

### 1.1 错误信息
```
Selenium 获取页面失败: Message: unknown error: net::ERR_SSL_PROTOCOL_ERROR
(Session info: chrome=148.0.7778.217)
```

### 1.2 当前实现现状
代码位置：`e:\DEVELOPERS\boonya-python-daily-2026\spider\web-to-doc\web_to_doc.py`

当前 `fetch_html_with_selenium()` 函数已经添加了 SSL 忽略参数：
- `--ignore-certificate-errors`
- `--ignore-ssl-errors`
- `--allow-insecure-localhost`

但这些参数仍然无法解决问题。

### 1.3 根本原因分析

**ERR_SSL_PROTOCOL_ERROR 的可能原因：**

1. **TLS 版本不兼容**
   - Chrome 148 默认禁用了 TLS 1.0/1.1
   - 目标网站可能只支持旧版 TLS 协议

2. **Chrome 版本过高**
   - Chrome 148 是较新版本，对 SSL/TLS 安全策略更严格
   - 需要启用对旧版 TLS 的支持

3. **代理或网络环境问题**
   - 企业网络、代理服务器可能导致 SSL 握手失败
   - 本地 SSL 证书链不完整

4. **Chrome 启动参数不足**
   - 需要更多参数来降低 SSL 验证级别

## 二、解决方案设计

### 2.1 方案一：增强 Chrome 启动参数（推荐）

**优点：**
- 最小改动
- 兼容性好
- 不影响其他功能

**需要添加的参数：**
```python
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_argument('--allow-insecure-localhost')
chrome_options.add_argument('--disable-web-security')  # 新增
chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')  # 新增
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_experimental_option('useAutomationExtension', False)  # 新增

# 降低 SSL 安全级别
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-infobars')
```

### 2.2 方案二：使用 Chrome DevTools Protocol

通过 CDP 命令忽略 SSL 错误：

```python
driver = webdriver.Chrome(service=Service(...), options=chrome_options)
driver.execute_cdp_cmd('Security.setIgnoreCertificateErrors', {'ignore': True})
```

### 2.3 方案三：降级 TLS 版本要求

强制 Chrome 接受所有 TLS 版本：

```python
chrome_options.add_argument('--ssl-version-min=tls1')  # 允许 TLS 1.0
chrome_options.add_argument('--ssl-version-max=tls1.3')
```

### 2.4 方案四：添加代理支持（如果需要）

如果用户网络环境需要代理：

```python
chrome_options.add_argument('--proxy-server=http://your-proxy:port')
chrome_options.add_argument('--proxy-bypass-list=<-loopback>')  # 本地地址不走代理
```

### 2.5 方案五：备用方案 - 使用 requests + 降级 SSL 验证

如果 Selenium 无法解决，可以使用 requests 作为降级方案：

```python
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

response = requests.get(url, verify=False, headers=HEADERS, timeout=10)
html = response.text
```

## 三、推荐实现方案（综合方案）

**修改文件：** `web_to_doc.py` 的 `fetch_html_with_selenium()` 函数

### 3.1 增强的启动参数

```python
def fetch_html_with_selenium(url):
    """
    使用 Selenium + Chrome 获取渲染后的完整 HTML
    优化 SSL 错误处理
    """
    chrome_options = Options()

    # 基础无头模式参数
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument(f'user-agent={HEADERS["User-Agent"]}')

    # ===== SSL/安全相关参数（增强版）=====
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--allow-insecure-localhost')
    chrome_options.add_argument('--disable-web-security')  # 关闭同源策略
    chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')

    # 降低安全级别
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')

    # TLS 版本支持
    chrome_options.add_argument('--ssl-version-min=tls1')

    # 实验性选项
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    try:
        # 使用 CDP 命令忽略证书错误
        driver.execute_cdp_cmd('Security.setIgnoreCertificateErrors', {'ignore': True})

        driver.get(url)
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        html = driver.page_source
    except Exception as e:
        print(f"❌ Selenium 获取页面失败: {e}")
        html = None
    finally:
        driver.quit()

    return html
```

### 3.2 添加降级方案

在主函数中添加降级逻辑：

```python
def main():
    url = 'https://blog.csdn.net/m0_65635427/article/details/130780280'
    print(f'🌐 正在抓取: {url}')

    # 1. 尝试 Selenium
    html = fetch_html_with_selenium(url)

    # 2. 如果 Selenium 失败，降级到 requests
    if not html:
        print("⚠️ Selenium 失败，尝试使用 requests 降级方案...")
        html = fetch_html_with_requests(url)

    if not html:
        print("❌ 无法获取页面，程序退出")
        return

    # 后续处理...
```

### 3.3 添加 requests 降级函数

```python
def fetch_html_with_requests(url):
    """
    使用 requests 作为降级方案（仅当 Selenium 失败时使用）
    忽略 SSL 验证
    """
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        response = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ Requests 获取页面失败: {e}")
        return None
```

## 四、诊断工具

添加调试模式，帮助诊断问题：

```python
def diagnose_ssl_issue(url):
    """
    诊断 SSL 连接问题
    """
    import ssl
    import socket
    from urllib.parse import urlparse

    parsed = urlparse(url)
    hostname = parsed.hostname
    port = parsed.port or 443

    print(f"🔍 诊断 SSL 连接: {hostname}:{port}")

    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                print(f"✅ SSL 连接成功")
                print(f"   TLS 版本: {ssock.version()}")
                print(f"   加密套件: {ssock.cipher()}")
    except Exception as e:
        print(f"❌ SSL 连接失败: {e}")
```

## 五、验证步骤

### 5.1 测试场景
1. 测试 CSDN 文章 URL
2. 测试其他 HTTPS 网站
3. 测试需要动态渲染的页面

### 5.2 预期结果
- 能够成功获取页面 HTML
- 不再出现 ERR_SSL_PROTOCOL_ERROR 错误
- 如果 Selenium 失败，自动降级到 requests

## 六、实施计划

| 步骤 | 任务 | 文件 | 改动内容 |
|------|------|------|----------|
| 1 | 增强启动参数 | `web_to_doc.py` | 修改 `fetch_html_with_selenium()` |
| 2 | 添加 CDP 命令 | `web_to_doc.py` | 在 driver 初始化后添加 |
| 3 | 添加降级函数 | `web_to_doc.py` | 新增 `fetch_html_with_requests()` |
| 4 | 修改主函数 | `web_to_doc.py` | 添加降级逻辑 |
| 5 | 添加诊断工具 | `web_to_doc.py` | 新增 `diagnose_ssl_issue()` |

## 七、注意事项

1. **安全性警告**
   - 禁用 SSL 验证会降低安全性
   - 仅在开发测试环境使用
   - 生产环境应使用正确的 SSL 证书

2. **Chrome 版本兼容性**
   - Chrome 148 是较新版本
   - 如果问题持续，可考虑使用稍旧版本的 ChromeDriver

3. **网络环境**
   - 检查是否有企业代理
   - 确认防火墙规则

## 八、总结

本设计提供了多层次的 SSL 错误解决方案：
1. 增强 Chrome 启动参数（主要方案）
2. 使用 CDP 命令忽略证书错误
3. 添加 requests 降级方案
4. 提供 SSL 诊断工具

推荐按顺序实施，逐步验证效果。