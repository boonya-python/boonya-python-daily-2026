import os
import time
import requests
from config import HEADERS, IMG_DIR, IMG_REQUEST_DELAY, REQUEST_TIMEOUT


class ImageDownloader:
    VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}

    def __init__(self, save_dir=IMG_DIR):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def download(self, img_url, save_path):
        try:
            resp = requests.get(img_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(resp.content)
                return True
        except Exception as e:
            print(f'  ⚠️ 下载失败: {img_url[:60]}... {e}')
        return False

    def download_all(self, img_urls):
        local_paths = []
        url_to_local = {}
        for i, url in enumerate(img_urls):
            ext = os.path.splitext(url.split('?')[0])[1]
            if not ext or ext.lower() not in self.VALID_EXTENSIONS:
                ext = '.jpg'
            filename = f'img_{i + 1:03d}{ext}'
            local_path = os.path.join(self.save_dir, filename)
            print(f'  📥 下载图片 {i + 1}/{len(img_urls)}: {filename}')
            if self.download(url, local_path):
                local_paths.append(local_path)
                url_to_local[url] = local_path
            time.sleep(IMG_REQUEST_DELAY)
        return local_paths, url_to_local
