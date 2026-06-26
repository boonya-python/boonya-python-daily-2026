import os
import time
import uuid


class PdfGenerator:
    def generate(self, docx_path, pdf_path):
        # 生成唯一临时文件，避免覆盖用户正在编辑的文档
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        unique_id = uuid.uuid4().hex[:6]
        temp_docx = docx_path.replace('.docx', f'_temp_{timestamp}_{unique_id}.docx')
        temp_pdf = pdf_path.replace('.pdf', f'_temp_{timestamp}_{unique_id}.pdf')

        # 复制原文件为临时文件
        import shutil
        shutil.copy2(docx_path, temp_docx)

        generators = [
            (self._from_docx2pdf, temp_docx, temp_pdf),
            (self._from_win32com, temp_docx, temp_pdf),
            (self._from_pdfkit, temp_docx, temp_pdf),
        ]

        result = False
        for gen, src, dst in generators:
            try:
                gen(src, dst)
                if os.path.exists(dst) and os.path.getsize(dst) > 0:
                    # 成功后将临时文件移动到目标位置
                    shutil.move(dst, pdf_path)
                    print(f'✅ PDF 已生成: {pdf_path}')
                    result = True
                    break
            except Exception as e:
                print(f"⚠️ {gen.__name__} 失败: {e}，尝试下一个方案")

        # 清理临时文件
        if os.path.exists(temp_docx):
            try:
                os.remove(temp_docx)
            except:
                pass
        if os.path.exists(temp_pdf) and not result:
            try:
                os.remove(temp_pdf)
            except:
                pass

        if not result:
            print("❌ 所有 PDF 生成方案均失败")
        return result

    def _from_docx2pdf(self, docx_path, pdf_path):
        from docx2pdf import convert
        convert(docx_path, pdf_path)

    def _from_win32com(self, docx_path, pdf_path):
        import win32com.client
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        try:
            doc = word.Documents.Open(os.path.abspath(docx_path))
            doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17)
            doc.Close()
        finally:
            word.Quit()

    def _from_pdfkit(self, docx_path, pdf_path):
        from docx import Document
        import pdfkit

        doc = Document(docx_path)
        html_parts = ['<html><head><meta charset="UTF-8"><style>']
        html_parts.append('body { font-family: "Microsoft YaHei", Arial, sans-serif; padding: 30px; line-height: 1.8; }')
        html_parts.append('img { max-width: 100%; height: auto; }')
        html_parts.append('pre, code { background: #f4f4f4; padding: 10px; border-radius: 4px; }')
        html_parts.append('</style></head><body>')

        for para in doc.paragraphs:
            if para.style.name.startswith('Heading'):
                level = para.style.name.replace('Heading ', '')
                html_parts.append(f'<h{level}>{para.text}</h{level}>')
            elif para.style.name == 'List Bullet':
                html_parts.append(f'<ul><li>{para.text}</li></ul>')
            elif para.style.name == 'List Number':
                html_parts.append(f'<ol><li>{para.text}</li></ol>')
            else:
                html_parts.append(f'<p>{para.text}</p>')

        html_parts.append('</body></html>')
        html_content = '\n'.join(html_parts)

        options = {
            'encoding': 'UTF-8',
            'page-size': 'A4',
            'margin-top': '15mm',
            'margin-bottom': '15mm',
            'margin-left': '15mm',
            'margin-right': '15mm',
        }
        pdfkit.from_string(html_content, pdf_path, options=options)
