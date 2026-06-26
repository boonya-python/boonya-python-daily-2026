以下是一个完整的 Python 爬虫程序，可将指定网页（以 CSDN 博客为例）的文章内容（含图片）抓取后导出为 PDF 和 Word 文档。

## 一、整体思路

1. 使用 `requests` + `BeautifulSoup` 爬取网页，提取文章标题、正文和图片链接
2. 图片先下载到本地临时目录，再嵌入文档
3. 使用 `pdfkit`（基于 wkhtmltopdf）生成 PDF
4. 使用 `python-docx` 生成 Word 文档

## 二、安装依赖

```bash
# 安装 Python 库
pip install requests beautifulsoup4 lxml python-docx pdfkit selenium webdriver-manager

# 下载并安装 wkhtmltopdf（PDF 转换核心工具）
# Windows: https://wkhtmltopdf.org/downloads.html
# macOS: brew install wkhtmltopdf
# Linux: sudo apt-get install wkhtmltopdf
```

安装完成后，将 wkhtmltopdf 的安装目录（如 `C:\Program Files\wkhtmltopdf\bin`）添加到系统环境变量 `PATH` 中。

## 三、完整代码

web_to_doc.py

## 四、运行说明

1. 将上述代码保存为 `web_to_doc.py`
2. 修改 `main()` 中的 `url` 变量为目标网页地址
3. 在终端执行：
   ```bash
   python web_to_doc.py
   ```

## 五、程序特点

| 功能 | 实现方式 |
|------|----------|
| **文章抓取** | requests + BeautifulSoup，支持 CSDN 的 `data-src` 懒加载图片 |
| **图片处理** | 自动下载到本地临时目录，再嵌入文档 |
| **PDF 生成** | pdfkit + wkhtmltopdf，保留完整样式和图片 |
| **Word 生成** | python-docx，保留标题层级、段落和图片 |

## 六、常见问题

**1. wkhtmltopdf 未找到**
- 下载安装后，将 `bin` 目录添加到系统 `PATH`
- 或在代码中指定路径：`config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')`，然后传入 `configuration=config`

**2. CSDN 反爬**
- 若请求被拒，可增加 Cookie（登录后从浏览器复制）
- 或使用 `selenium` 模拟浏览器渲染

**3. 图片未显示**
- 检查 `IMG_DIR` 目录是否有写入权限
- Word 中的图片宽度可调整 `Inches()` 参数

**4. 其他网站适配**
- 修改 `parse_article()` 中的选择器，匹配目标网站的标题和正文容器即可