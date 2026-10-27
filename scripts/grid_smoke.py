"""Два независимых клиента Remote WebDriver одновременно."""
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from selenium import webdriver
from tests.pages.planner import PlannerPage


def check(number):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    driver = webdriver.Remote(command_executor=os.environ.get('SELENIUM_REMOTE_URL', 'http://127.0.0.1:4444'), options=options)
    try:
        page = PlannerPage(driver, os.environ.get('BASE_URL', 'http://127.0.0.1:8000'))
        title = f'Клиент Grid {number}'
        page.open().login().ready().add(title)
        assert page.titles() == [title]
        return {'client': number, 'session': driver.session_id, 'result': 'PASS'}
    finally:
        driver.quit()


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=2) as pool:
        print(json.dumps(list(pool.map(check, [1, 2])), ensure_ascii=False, indent=2))
