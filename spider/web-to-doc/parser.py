from bs4 import BeautifulSoup
from urllib.parse import urljoin


def _clean_content(tag):
    for t in tag.find_all(['style', 'script', 'noscript', 'svg', 'canvas']):
        t.decompose()
    return tag


class CSDNArticleParser:
    TITLE_SELECTORS = [
        {'name': 'h1', 'class_': 'title-article'},
        {'name': 'h1', 'class_': 'blog-title'},
        {'name': 'h1'},
    ]

    CONTENT_SELECTORS = [
        {'name': 'div', 'id': 'article_content'},
        {'name': 'div', 'class_': 'article_content'},
        {'name': 'div', 'id': 'content_views'},
    ]

    def parse(self, html, base_url):
        soup = BeautifulSoup(html, 'lxml')
        title = self._extract_title(soup)
        content_div = self._extract_content(soup)
        img_urls = self._extract_images(content_div, base_url)
        return title, content_div, img_urls

    def _extract_title(self, soup):
        for selector in self.TITLE_SELECTORS:
            tag = soup.find(**selector)
            if tag:
                return tag.get_text().strip()
        return '未命名文章'

    def _extract_content(self, soup):
        for selector in self.CONTENT_SELECTORS:
            tag = soup.find(**selector)
            if tag:
                return _clean_content(tag)
        all_divs = soup.find_all('div')
        if all_divs:
            return _clean_content(max(all_divs, key=lambda d: len(d.get_text(strip=True))))
        return None

    def _extract_images(self, content_div, base_url):
        img_urls = []
        if not content_div:
            return img_urls
        for img in content_div.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src and not src.startswith('data:'):
                full_url = urljoin(base_url, src)
                img_urls.append(full_url)
        return img_urls


class CnblogsArticleParser:
    """博客园文章解析器"""
    TITLE_SELECTORS = [
        {'name': 'h1', 'class_': 'post-title'},
        {'name': 'h1', 'class_': 'entry-title'},
        {'name': 'h1'},
    ]

    CONTENT_SELECTORS = [
        {'name': 'div', 'class_': 'blogpost-body'},
        {'name': 'div', 'class_': 'post-body'},
        {'name': 'div', 'id': 'cnblogs_post_body'},
        {'name': 'article'},
    ]

    def parse(self, html, base_url):
        soup = BeautifulSoup(html, 'lxml')
        title = self._extract_title(soup)
        content_div = self._extract_content(soup)
        img_urls = self._extract_images(content_div, base_url)
        return title, content_div, img_urls

    def _extract_title(self, soup):
        for selector in self.TITLE_SELECTORS:
            tag = soup.find(**selector)
            if tag:
                return tag.get_text().strip()
        return '未命名文章'

    def _extract_content(self, soup):
        for selector in self.CONTENT_SELECTORS:
            tag = soup.find(**selector)
            if tag:
                return _clean_content(tag)
        main = soup.find('div', class_='main')
        if main:
            return _clean_content(main)
        all_divs = soup.find_all('div')
        if all_divs:
            return _clean_content(max(all_divs, key=lambda d: len(d.get_text(strip=True))))
        return None

    def _extract_images(self, content_div, base_url):
        img_urls = []
        if not content_div:
            return img_urls
        for img in content_div.find_all('img'):
            src = img.get('src') or img.get('data-src') or img.get('original')
            if src and not src.startswith('data:'):
                full_url = urljoin(base_url, src)
                img_urls.append(full_url)
        return img_urls


def get_parser(url):
    """根据 URL 自动选择解析器"""
    if 'cnblogs.com' in url:
        return CnblogsArticleParser()
    return CSDNArticleParser()
