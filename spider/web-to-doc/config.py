import os

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

IMG_DIR = './temp_images'
os.makedirs(IMG_DIR, exist_ok=True)

DEFAULT_WAIT_TIME = 3
SCROLL_WAIT_TIME = 1.5
IMG_REQUEST_DELAY = 0.3
REQUEST_TIMEOUT = 15
