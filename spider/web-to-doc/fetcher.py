import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config import HEADERS, DEFAULT_WAIT_TIME, SCROLL_WAIT_TIME, REQUEST_TIMEOUT


class SeleniumFetcher:
    def __init__(self, headless=True):
        self.headless = headless

    def _build_options(self):
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument(f'user-agent={HEADERS["User-Agent"]}')

        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--allow-insecure-localhost')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        options.add_argument('--ssl-version-min=tls1')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')

        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        return options

    def fetch(self, url, wait_time=DEFAULT_WAIT_TIME, scroll=True):
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self._build_options()
        )
        try:
            driver.execute_cdp_cmd('Security.setIgnoreCertificateErrors', {'ignore': True})
            driver.get(url)
            time.sleep(wait_time)
            if scroll:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(SCROLL_WAIT_TIME)
            return driver.page_source
        finally:
            driver.quit()


class RequestsFetcher:
    def fetch(self, url):
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, verify=False)
        resp.raise_for_status()
        return resp.text


def fetch_html(url, use_selenium=True):
    if use_selenium:
        try:
            return SeleniumFetcher().fetch(url)
        except Exception as e:
            print(f"⚠️ Selenium 失败: {e}，降级到 requests")
    return RequestsFetcher().fetch(url)
