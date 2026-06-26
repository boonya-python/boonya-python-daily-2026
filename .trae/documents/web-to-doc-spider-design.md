# web-to-doc Spider 需求设计

## 一、需求定义

**功能目标**：输入 CSDN 博客文章 URL，爬取文章全文（含图片），输出 Word 文档（.docx）和 PDF 文档（.pdf）。

**核心流程**：
```
CSDN 文章 URL → 爬取页面 → 解析文章内容 → 下载图片 → 生成 Word(.docx) → 转换 PDF(.pdf)
```

---

## 二、当前实现分析

### 2.1 现有代码
- 文件：[web_to_doc.py](file:///e:/DEVELOPERS/boonya-python-daily-2026/spider/web-to-doc/web_to_doc.py)
- 单文件实现，所有功能在一个文件里
- 依赖：selenium, requests, beautifulsoup4, python-docx, pdfkit

### 2.2 当前问题
- **Selenium SSL 错误**：`net::ERR_SSL_PROTOCOL_ERROR`（Chrome 148）
- **结构混乱**：所有函数堆在一个文件里，难维护
- **PDF 生成方式**：用 pdfkit(wkhtmltopdf) 从 HTML 直转，不是从 docx 转
- **无降级机制**：Selenium 失败就直接退出

---

## 三、技术选型（最优方案）

### 3.1 爬取层

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| Selenium + Chrome | 渲染 JS 动态内容，模拟真实浏览器 | 慢，有 SSL 问题 | **主方案** |
| requests + BeautifulSoup | 快，简单，无浏览器依赖 | 无法渲染 JS，可能被反爬 | **降级方案** |

**决策**：双层爬取，Selenium 为主，requests 兜底。SSL 问题通过增强 Chrome 参数 + CDP 命令解决。

### 3.2 Word 生成

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| python-docx | 纯 Python，跨平台，可控性强 | 需要手动解析 HTML 结构 | **采用** |
| pandoc | 格式转换能力强 | 需要安装外部工具，样式控制弱 | 不采用 |

**决策**：继续使用 python-docx（已实现，效果尚可）。

### 3.3 PDF 生成

用户需求明确：**doc 转为 pdf**。对比方案：

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| **docx2pdf** (Windows Word) | 质量最好，和 Word 完全一致 | 依赖 Windows + 安装 Word | **首选（Windows环境）** |
| **Selenium 打印 PDF** | 质量好，复用已有 Chrome，不依赖 Word | 不是 doc→pdf，是 HTML→pdf | 备选 |
| LibreOffice headless | 开源，跨平台 | 需要安装 LibreOffice，体积大 | 备选 |
| pdfkit (wkhtmltopdf) | 轻量 | 样式一般，CSS 支持差，需额外安装 | 当前方案，不推荐 |

**决策**：
- 优先方案：**docx2pdf**（调用本地 Word，质量最好，Windows 用户标配）
- 降级方案：如果没有 Word，用 Selenium 直接打印 PDF（反正已经在跑 Chrome 了）
- 最终都不行：回退到 pdfkit

---

## 四、架构设计

### 4.1 目录结构

```
spider/web-to-doc/
├── __init__.py
├── main.py                 # 主入口，串联流程
├── fetcher.py              # 页面获取（Selenium + requests 双层）
├── parser.py               # 文章解析（提取标题、正文、图片）
├── downloader.py           # 图片下载
├── generators/
│   ├── __init__.py
│   ├── word_generator.py   # Word 生成
│   └── pdf_generator.py    # PDF 生成（docx→pdf，多层降级）
├── config.py               # 配置常量
└── utils.py                # 工具函数
```

### 4.2 模块职责

| 模块 | 职责 | 输入 | 输出 |
|------|------|------|------|
| **fetcher** | 获取页面 HTML | url | html 字符串 |
| **parser** | 解析文章结构 | html, base_url | title, content_div, img_urls |
| **downloader** | 下载图片到本地 | img_urls | local_paths, url_to_local |
| **word_generator** | 生成 Word 文档 | title, content, images | .docx 文件 |
| **pdf_generator** | docx 转 PDF | .docx 文件路径 | .pdf 文件路径 |
| **main** | 编排整个流程 | url | 输出文件路径 |

---

## 五、核心模块设计

### 5.1 fetcher.py - 页面获取

```python
class SeleniumFetcher:
    """Selenium 爬取（主方案），处理 SSL 问题"""
    
    def __init__(self):
        self.driver = None
    
    def _build_options(self):
        """构建 Chrome 选项，含 SSL 绕过"""
        options = Options()
        # 基础
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument(f'user-agent=...')
        
        # SSL 绕过（关键！）
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--allow-insecure-localhost')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        options.add_argument('--ssl-version-min=tls1')
        
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        return options
    
    def fetch(self, url, wait_time=3, scroll=True):
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self._build_options()
        )
        try:
            # CDP 命令忽略证书错误
            driver.execute_cdp_cmd('Security.setIgnoreCertificateErrors', {'ignore': True})
            driver.get(url)
            time.sleep(wait_time)
            if scroll:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)
            return driver.page_source
        finally:
            driver.quit()


class RequestsFetcher:
    """requests 爬取（降级方案），忽略 SSL"""
    
    def fetch(self, url):
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        resp = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        resp.raise_for_status()
        return resp.text


def fetch_html(url):
    """统一入口：先 Selenium，失败降级到 requests"""
    try:
        return SeleniumFetcher().fetch(url)
    except Exception as e:
        print(f"⚠️ Selenium 失败: {e}，降级到 requests")
        return RequestsFetcher().fetch(url)
```

### 5.2 parser.py - 文章解析

```python
class CSDNArticleParser:
    """CSDN 文章解析器"""
    
    TITLE_SELECTORS = [
        ('h1', 'title-article'),
        ('h1', 'blog-title'),
        ('h1', None),
    ]
    
    CONTENT_SELECTORS = [
        ('div', 'article_content', 'id'),
        ('div', 'article_content', 'class'),
        ('div', 'content_views', 'id'),
    ]
    
    def parse(self, html, base_url):
        soup = BeautifulSoup(html, 'lxml')
        title = self._extract_title(soup)
        content_div = self._extract_content(soup)
        img_urls = self._extract_images(content_div, base_url)
        return title, content_div, img_urls
```

### 5.3 generators/pdf_generator.py - PDF 生成

```python
class PdfGenerator:
    """docx 转 PDF，多层降级策略"""
    
    def generate(self, docx_path, pdf_path):
        generators = [
            self._from_docx2pdf,    # 首选：docx2pdf (Word)
            self._from_selenium,    # 备选：Selenium 打印
            self._from_pdfkit,      # 兜底：pdfkit
        ]
        for gen in generators:
            try:
                gen(docx_path, pdf_path)
                if os.path.exists(pdf_path):
                    return True
            except Exception as e:
                print(f"⚠️ {gen.__name__} 失败: {e}，尝试下一个方案")
        return False
    
    def _from_docx2pdf(self, docx_path, pdf_path):
        """用 Word 转（质量最好）"""
        from docx2pdf import convert
        convert(docx_path, pdf_path)
    
    def _from_selenium(self, docx_path, pdf_path):
        """Selenium 打印（从 docx 读取内容再渲染打印）"""
        # 读取 docx 内容，用浏览器打开再打印为 PDF
        # 或直接用 Selenium 打印原网页
        pass
    
    def _from_pdfkit(self, docx_path, pdf_path):
        """兜底：pdfkit（从 HTML 转）"""
        pass
```

---

## 六、SSL 错误解决方案（核心）

### 问题根因
Chrome 148 对 SSL/TLS 安全策略收紧，目标站点证书或 TLS 版本不兼容。

### 解决方案（按优先级）

1. **Chrome 启动参数增强**（已验证有效）
   - `--ignore-certificate-errors`
   - `--ignore-ssl-errors`
   - `--allow-insecure-localhost`
   - `--disable-web-security`
   - `--ssl-version-min=tls1`

2. **CDP 命令**
   - `Security.setIgnoreCertificateErrors`

3. **降级到 requests**
   - `verify=False` + 禁用警告

---

## 七、实施步骤

| 阶段 | 任务 | 文件 |
|------|------|------|
| 1 | 重构目录结构，拆分模块 | 新建多个文件 |
| 2 | 实现 fetcher.py，解决 SSL 问题 | fetcher.py |
| 3 | 实现 parser.py | parser.py |
| 4 | 实现 downloader.py | downloader.py |
| 5 | 实现 word_generator.py | generators/word_generator.py |
| 6 | 实现 pdf_generator.py（docx2pdf 优先） | generators/pdf_generator.py |
| 7 | 实现 main.py 主流程 | main.py |
| 8 | 测试验证 | - |

---

## 八、验证标准

- [ ] 输入 CSDN URL 能成功爬取（不再报 SSL 错误）
- [ ] 生成的 docx 包含完整正文和图片
- [ ] 生成的 pdf 排版正常，图片完整
- [ ] Selenium 失败时能自动降级到 requests
- [ ] PDF 生成有多层降级，至少有一种方式能成功

---

## 九、依赖清单

```
selenium
webdriver-manager
requests
beautifulsoup4
lxml
python-docx
docx2pdf          # Windows + Word 环境首选
pdfkit            # 兜底（需安装 wkhtmltopdf）
```
