#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from md_parser import parse_markdown, fix_image_paths
from pdf_generator import PdfGenerator
from utils import build_output_path


def convert_md_to_pdf(md_path, output_dir=None):
    print(f'📄 正在处理: {md_path}')

    title, html_content, img_paths = parse_markdown(md_path)
    print(f'   标题: {title}')
    print(f'   发现 {len(img_paths)} 张图片')

    base_dir = os.path.dirname(os.path.abspath(md_path))
    html_content = fix_image_paths(html_content, base_dir)

    output_path = build_output_path(md_path, output_dir)

    pdf_gen = PdfGenerator()
    success = pdf_gen.generate(html_content, output_path)

    return success, output_path


def find_md_files(input_path):
    md_files = []
    if os.path.isfile(input_path) and input_path.endswith('.md'):
        md_files.append(input_path)
    elif os.path.isdir(input_path):
        for root, dirs, files in os.walk(input_path):
            for file in files:
                if file.endswith('.md'):
                    md_files.append(os.path.join(root, file))
    return md_files


def main():
    parser = argparse.ArgumentParser(description='本地 Markdown 转 PDF 工具')
    parser.add_argument('input', help='输入文件路径或目录')
    parser.add_argument('-o', '--output', default=None, help='输出目录（默认与输入文件同目录）')
    args = parser.parse_args()

    md_files = find_md_files(args.input)

    if not md_files:
        print('❌ 未找到任何 markdown 文件')
        return

    print(f'📁 共发现 {len(md_files)} 个 markdown 文件')

    success_count = 0
    failed_files = []

    for md_file in md_files:
        try:
            success, output_path = convert_md_to_pdf(md_file, args.output)
            if success:
                success_count += 1
                print(f'   ✅ 成功: {output_path}')
            else:
                failed_files.append(md_file)
                print(f'   ❌ 失败: {md_file}')
        except Exception as e:
            failed_files.append(md_file)
            print(f'   ❌ 错误: {md_file} - {e}')
        print()

    print('\n🎉 处理完成！')
    print(f'   成功: {success_count} 个')
    print(f'   失败: {len(failed_files)} 个')

    if failed_files:
        print('\n失败的文件:')
        for f in failed_files:
            print(f'   - {f}')


if __name__ == '__main__':
    main()