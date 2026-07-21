import os
import re
import markdown
from bs4 import BeautifulSoup


def parse_markdown(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    base_dir = os.path.dirname(os.path.abspath(md_path))
    html_content = md_to_html(md_content)
    img_paths = extract_images(md_content, base_dir)

    title = extract_title(md_content)

    return title, html_content, img_paths


def extract_title(md_content):
    lines = md_content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return '未命名文档'


def extract_images(md_content, base_dir):
    img_pattern = r'!\[.*?\]\((.*?)\)'
    matches = re.findall(img_pattern, md_content)

    img_paths = []
    for match in matches:
        img_path = match.strip()
        if img_path.startswith('http://') or img_path.startswith('https://'):
            continue

        if not os.path.isabs(img_path):
            img_path = os.path.join(base_dir, img_path)

        img_path = os.path.normpath(img_path)
        if os.path.exists(img_path):
            img_paths.append(img_path)

    return img_paths


def md_to_html(md_content):
    return markdown.markdown(md_content, extensions=['fenced_code', 'tables'])


def fix_image_paths(html_content, base_dir):
    soup = BeautifulSoup(html_content, 'html.parser')

    for img in soup.find_all('img'):
        src = img.get('src')
        if src and not src.startswith('http://') and not src.startswith('https://'):
            if not os.path.isabs(src):
                abs_path = os.path.normpath(os.path.join(base_dir, src))
                img['src'] = abs_path

    return str(soup)