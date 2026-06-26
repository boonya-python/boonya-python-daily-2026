#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetcher import fetch_html
from parser import CSDNArticleParser
from downloader import ImageDownloader
from generators import WordGenerator, PdfGenerator


def safe_filename(title):
    return "".join(c for c in title if c not in r'\/:*?"<>|')


def run(url, output_dir='.'):
    print(f'🌐 正在抓取: {url}')

    html = fetch_html(url)
    if not html:
        print("❌ 无法获取页面，程序退出")
        return

    parser = CSDNArticleParser()
    title, content_div, img_urls = parser.parse(html, url)
    print(f'📄 标题: {title}')
    print(f'🖼️  发现 {len(img_urls)} 张图片')

    downloader = ImageDownloader()
    img_paths, url_to_local = downloader.download_all(img_urls)
    print(f'✅ 成功下载 {len(img_paths)} 张图片')

    safe_title = safe_filename(title)
    word_path = os.path.join(output_dir, f'{safe_title}.docx')

    word_gen = WordGenerator()
    word_gen.generate(title, content_div, url_to_local, word_path)

    pdf_path = os.path.join(output_dir, f'{safe_title}.pdf')
    pdf_gen = PdfGenerator()
    pdf_gen.generate(word_path, pdf_path)

    print('\n🎉 完成！')
    print(f'   Word: {word_path}')
    print(f'   PDF:  {pdf_path}')


def main():
    url = 'https://blog.csdn.net/m0_65635427/article/details/130780280'
    run(url)


if __name__ == '__main__':
    main()
