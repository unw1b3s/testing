"""Проверка интерфейса при подмене health через отдельный прокси Charles."""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tests.pages.planner import PlannerPage

mode = sys.argv[1]
expected = {'rewrite': 'Технические работы (Rewrite)', 'map-local': 'Технические работы (Map Local)', 'breakpoint': 'Технические работы (вручную)'}[mode]
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--proxy-server=http://127.0.0.1:8899')
options.add_argument('--proxy-bypass-list=<-loopback>')
driver = webdriver.Chrome(options=options)
driver.set_window_size(1280, 900)
try:
    page = PlannerPage(driver, 'http://127.0.0.1:8000').open()
    page.login()
    page.wait = WebDriverWait(driver, 180 if mode == 'breakpoint' else 8)
    page.wait.until(EC.text_to_be_present_in_element((By.ID, 'service-status'), expected))
    actual = driver.find_element(By.ID, 'service-status').text
    driver.save_screenshot(f'evidence/charles/{mode}.png')
    Path(f'evidence/charles/{mode}-ui.json').write_text(json.dumps({'time': datetime.now(timezone.utc).isoformat(), 'expected': expected, 'actual': actual, 'result': 'PASS'}, ensure_ascii=False, indent=2))
    print(actual)
finally:
    driver.quit()
