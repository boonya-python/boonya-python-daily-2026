# markdown_to_pdf

本地 Markdown 文件转 PDF 工具，支持解析 markdown 中的本地图片引用并一并转换为 PDF。

## 功能特性

- 支持单文件和目录批量转换
- 自动解析 markdown 中的本地图片引用（相对路径/绝对路径）
- 三种 PDF 生成方案自动降级：pdfkit → docx2pdf → win32com
- 输出文件名带时间戳，避免覆盖之前的生成结果
- 支持中文内容和表格渲染

## 环境要求

- Python 3.8+
- Windows 系统（docx2pdf 和 win32com 方案需要）

## 安装依赖

```bash
pip install markdown pdfkit beautifulsoup4 python-docx docx2pdf pywin32
```

### 可选依赖

- **wkhtmltopdf**：pdfkit 方案需要安装 wkhtmltopdf 并添加到 PATH
  - 下载地址：https://wkhtmltopdf.org/downloads.html

## 使用方法

### 命令行参数

```bash
python -m markdown_to_pdf.main <input> [-o <output_dir>]
```

| 参数 | 说明 |
|------|------|
| `<input>` | 输入文件路径或目录（必须） |
| `-o, --output` | 输出目录（可选，默认与输入文件同目录） |

### 使用示例

#### 1. 转换单个 markdown 文件

```bash
python -m markdown_to_pdf.main ./docs/guide.md -o ./output
```

输出文件：`./output/guide_20260720_180402.pdf`

#### 2. 转换目录下所有 markdown 文件

```bash
python -m markdown_to_pdf.main ./docs -o ./output
```

#### 3. 使用默认输出目录（同输入文件目录）

```bash
python -m markdown_to_pdf.main ./docs/guide.md
```

输出文件：`./docs/guide_20260720_180402.pdf`

## 测试

### 测试步骤

1. **准备测试文件**：在项目根目录下创建测试目录

```bash
mkdir -p ./test_data
```

2. **创建测试 markdown 文件** `./test_data/test.md`：

```markdown
# 测试文档

这是一个测试文档。

## 图片测试

![测试图片](img.png)

## 表格测试

| 列1 | 列2 | 列3 |
|-----|-----|-----|
| A | B | C |
| D | E | F |

## 代码测试

```python
def hello():
    print("Hello, World!")
```
```

3. **添加测试图片**：在 `./test_data/` 目录下放置一张名为 `img.png` 的图片

4. **运行测试**：

```bash
python -m markdown_to_pdf.main ./test_data/test.md -o ./test_output
```

5. **验证结果**：

```bash
ls ./test_output/
# 应该看到类似：test_20260720_180402.pdf
```

### 示例测试

使用项目外的真实文件测试：

```bash
python -m markdown_to_pdf.main "E:\AI\java\hrgk-radar-backend\hrgk-radar-deploy\aliyun\IKEv2VPN.md" -o "E:\AI\java\hrgk-radar-backend\hrgk-radar-deploy\aliyun"
```

测试结果：
- 成功识别 6 张本地图片
- 生成 PDF 文件：`IKEv2VPN_20260720_180402.pdf`

## 输出文件命名规则

```
{原文件名}_{时间戳}.pdf
```

时间戳格式：`YYYYMMDD_HHMMSS`

示例：
```
README_20260720_180402.pdf
guide_20260720_180500.pdf
```

## 模块结构

```
markdown_to_pdf/
├── __init__.py       # 模块初始化
├── main.py           # 主入口，命令行参数处理
├── md_parser.py      # Markdown 解析器
├── pdf_generator.py  # PDF 生成器
└── utils.py          # 工具函数
```

## PDF 生成方案优先级

1. **pdfkit**：使用 wkhtmltopdf 直接从 HTML 生成 PDF
2. **docx2pdf**：先转为 Word 文档，再转换为 PDF
3. **win32com**：使用 Microsoft Word COM 接口转换

工具会自动尝试第一种方案，失败后依次尝试下一种，直到成功。

## 注意事项

1. **图片路径**：markdown 中的图片引用支持相对路径和绝对路径
2. **网络图片**：暂不支持网络图片（http/https），仅处理本地图片
3. **中文支持**：已配置中文字体（Microsoft YaHei、PingFang SC）
4. **输出目录**：输出目录不存在时会自动创建

## 许可证

MIT License