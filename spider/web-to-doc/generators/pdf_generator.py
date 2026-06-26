import os


class PdfGenerator:
    def generate(self, docx_path, pdf_path):
        generators = [
            self._from_docx2pdf,
            self._from_win32com,
            self._from_pdfkit,
        ]
        for gen in generators:
            try:
                gen(docx_path, pdf_path)
                if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                    print(f'✅ PDF 已生成: {pdf_path}')
                    return True
            except Exception as e:
                print(f"⚠️ {gen.__name__} 失败: {e}，尝试下一个方案")
        print("❌ 所有 PDF 生成方案均失败")
        return False

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
