# 本地 Markdown 转 PDF 实现计划

## 一、需求分析

### 1.1 用户需求
- 将本地目录中的 markdown 文件及其内部引用的图片一并转换为 PDF
- 每个文件必须有独立的输出路径，不能覆盖之前生成的文件
- 每个输出文件需要包含时间戳，确保唯一性

### 1.2 参考代码分析
参考 `spider/web-to-doc/` 中的 web-to-pdf 实现：
- 使用 `pdfkit` 通过 HTML 生成 PDF
- 使用 `docx2pdf`/`win32com` 通过 Word 生成 PDF（备选方案）
- 使用 `BeautifulSoup` 处理 HTML 内容
- 图片路径处理机制

### 1.3 技术关键点
- Markdown 解析：需要将 md 文件转为 HTML
- 图片引用处理：解析 markdown 中的 `![](path)` 语法，处理相对路径和绝对路径
- 输出路径：每个文件独立输出，带时间戳

---

## 二、实现方案

### 2.1 模块结构设计

在项目根目录下创建新模块 `markdown_to_pdf/`：

```
markdown_to_pdf/
├── __init__.py
├── main.py           # 入口脚本，处理命令行参数
├── md_parser.py      # Markdown 解析器，提取内容和图片引用
├── pdf_generator.py  # PDF 生成器，参考 spider 的实现
└── utils.py          # 工具函数（文件名安全处理、时间戳等）
```

### 2.2 核心流程

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 读取 markdown 文件                                       │
├─────────────────────────────────────────────────────────────┤
│ 2. 解析 markdown，提取所有图片引用（相对路径/绝对路径）       │
├─────────────────────────────────────────────────────────────┤
│ 3. 将 markdown 转换为 HTML（保留图片引用）                   │
├─────────────────────────────────────────────────────────────┤
│ 4. 将 HTML 中的图片路径替换为完整本地路径                     │
├─────────────────────────────────────────────────────────────┤
│ 5. 使用 pdfkit 生成 PDF（带时间戳的输出文件名）              │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 关键函数设计

#### 2.3.1 md_parser.py

| 函数名 | 功能 | 参数 | 返回值 |
|--------|------|------|--------|
| `parse_markdown(md_path)` | 解析 markdown 文件 | `md_path`: markdown 文件路径 | `(title, html_content, img_paths)` |
| `extract_images(md_content, base_dir)` | 提取 markdown 中的图片路径 | `md_content`: markdown 内容, `base_dir`: 基础目录 | `list[str]` 图片完整路径列表 |
| `md_to_html(md_content)` | markdown 转 HTML | `md_content`: markdown 内容 | `str` HTML 字符串 |

#### 2.3.2 pdf_generator.py

| 函数名 | 功能 | 参数 | 返回值 |
|--------|------|------|--------|
| `generate(html_content, img_paths, output_path)` | 生成 PDF | `html_content`: HTML 内容, `img_paths`: 图片路径映射, `output_path`: 输出路径 | `bool` 是否成功 |

#### 2.3.3 utils.py

| 函数名 | 功能 | 参数 | 返回值 |
|--------|------|------|--------|
| `safe_filename(name)` | 清理文件名中的非法字符 | `name`: 原始文件名 | `str` 安全文件名 |
| `get_timestamp()` | 获取时间戳字符串 | 无 | `str` 格式：`YYYYMMDD_HHMMSS` |
| `build_output_path(input_path, output_dir)` | 构建带时间戳的输出路径 | `input_path`: 输入文件路径, `output_dir`: 输出目录 | `str` 输出文件完整路径 |

---

## 三、文件修改清单

### 3.1 新建文件

| 文件路径 | 说明 |
|----------|------|
| `markdown_to_pdf/__init__.py` | 模块初始化文件 |
| `markdown_to_pdf/main.py` | 主入口，支持命令行参数 |
| `markdown_to_pdf/md_parser.py` | Markdown 解析和图片提取 |
| `markdown_to_pdf/pdf_generator.py` | PDF 生成器 |
| `markdown_to_pdf/utils.py` | 工具函数 |

### 3.2 修改文件

| 文件路径 | 修改内容 |
|----------|----------|
| `main.py` | 添加 markdown-to-pdf 模块的调用入口（可选） |

---

## 四、步骤分解

### 步骤 1：创建模块目录和初始化文件
- 创建 `markdown_to_pdf/` 目录
- 创建 `__init__.py`

### 步骤 2：实现工具函数 utils.py
- `safe_filename()` - 清理非法字符
- `get_timestamp()` - 获取时间戳
- `build_output_path()` - 构建输出路径

### 步骤 3：实现 Markdown 解析器 md_parser.py
- 使用 `markdown` 库将 md 转为 HTML
- 使用正则表达式提取图片引用
- 处理相对路径转换为绝对路径

### 步骤 4：实现 PDF 生成器 pdf_generator.py
- 参考 `spider/web-to-doc/generators/pdf_generator.py` 的实现
- 修改为直接从 HTML 生成 PDF
- 支持本地图片路径

### 步骤 5：实现主入口 main.py
- 命令行参数解析（输入文件/目录、输出目录）
- 遍历处理多个 markdown 文件
- 调用解析器和生成器

---

## 五、依赖与环境

### 5.1 需要安装的依赖
```bash
pip install markdown
pip install pdfkit
pip install beautifulsoup4
```

### 5.2 外部依赖
- `wkhtmltopdf`：pdfkit 需要的命令行工具，需安装并添加到 PATH

---

## 六、风险与注意事项

### 6.1 风险点
| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 图片路径为相对路径 | PDF 中图片无法显示 | 统一转换为绝对路径 |
| markdown 中引用网络图片 | 需要下载或处理 | 暂不支持，仅处理本地图片 |
| 输出文件重名覆盖 | 丢失之前的生成结果 | 强制添加时间戳 |
| wkhtmltopdf 未安装 | PDF 生成失败 | 添加错误提示和安装指引 |

### 6.2 注意事项
- 图片路径需要使用绝对路径
- PDF 生成时需要设置 `enable-local-file-access` 选项
- 中文支持需要正确设置字体和编码

---

## 七、测试方案

### 7.1 测试用例
1. **单文件转换**：转换一个简单的 markdown 文件（含文本和图片）
2. **多文件转换**：转换目录下多个 markdown 文件，验证输出文件名唯一性
3. **相对路径图片**：测试 markdown 中引用相对路径的图片
4. **绝对路径图片**：测试 markdown 中引用绝对路径的图片

### 7.2 验证标准
- 生成的 PDF 文件存在且大小 > 0
- PDF 中包含完整的文本内容
- PDF 中图片正确显示
- 输出文件名包含时间戳，不会覆盖已有文件

---

## 八、输出格式

### 8.1 命令行使用方式
```bash
# 转换单个文件
python -m markdown_to_pdf input.md -o ./output

# 转换目录下所有 md 文件
python -m markdown_to_pdf ./docs -o ./output

# 使用默认输出目录（同输入目录）
python -m markdown_to_pdf input.md
```

### 8.2 输出文件命名规则
```
{原文件名}_{时间戳}.pdf
```
示例：
```
README_20240115_143022.pdf
```