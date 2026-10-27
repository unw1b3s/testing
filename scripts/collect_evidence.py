"""Снимки экрана, размеры viewport и сетевые события Chrome DevTools Protocol."""
import base64
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from tests.pages.planner import PlannerPage

out = Path(sys.argv[1] if len(sys.argv) > 1 else 'evidence')
(out / 'screenshots').mkdir(parents=True, exist_ok=True)
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
driver = webdriver.Chrome(options=options)
driver.set_window_size(1280, 900)
results = {'time': datetime.now(timezone.utc).isoformat(), 'browser': driver.capabilities['browserVersion'], 'viewport': []}
try:
    driver.execute_cdp_cmd('Network.enable', {})
    page = PlannerPage(driver, os.environ.get('BASE_URL', 'http://127.0.0.1:8000')).open()
    driver.save_screenshot(str(out / 'screenshots/login.png'))
    page.login(password='Wrong123!')
    assert page.error() == 'Неверная почта или пароль'
    driver.save_screenshot(str(out / 'screenshots/wrong-password.png'))
    page.login().ready().add('Подготовить практическую работу', 'Высокий')
    driver.save_screenshot(str(out / 'screenshots/tasks.png'))
    events = [json.loads(entry['message'])['message'] for entry in driver.get_log('performance')]
    selected = []
    for event in events:
        params = event['params']
        if event['method'] in ('Network.requestWillBeSent', 'Network.responseReceived') and '/api/' in params.get('request', params.get('response', {})).get('url', ''):
            if 'request' in params:
                params['request']['headers'].pop('Cookie', None)
            selected.append(event)
    # Только health: в нём нет пароля и cookie.
    health = [event for event in selected if '/api/health' in event['params'].get('request', event['params'].get('response', {})).get('url', '')]
    for event in health:
        if event['method'] == 'Network.responseReceived':
            event['body'] = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': event['params']['requestId']})
    (out / 'http-devtools.json').write_text(json.dumps(health, ensure_ascii=False, indent=2))
    long_title = 'Я' * 80
    page.add(long_title)
    for width, height in [(320, 568), (375, 812), (768, 1024), (1280, 720), (1920, 1080)]:
        driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {'width': width, 'height': height, 'deviceScaleFactor': 1, 'mobile': width < 600})
        measurement = driver.execute_script('return {width: innerWidth, document: document.documentElement.scrollWidth, height: innerHeight}')
        measurement['pass'] = measurement['document'] <= width
        results['viewport'].append(measurement)
        driver.save_screenshot(str(out / f'screenshots/viewport-{width}.png'))
        metrics = driver.execute_cdp_cmd('Page.getLayoutMetrics', {})['cssContentSize']
        shot = driver.execute_cdp_cmd('Page.captureScreenshot', {'captureBeyondViewport': True, 'clip': {**metrics, 'scale': 1}})
        (out / f'screenshots/full-{width}.png').write_bytes(base64.b64decode(shot['data']))
    driver.execute_cdp_cmd('Emulation.clearDeviceMetricsOverride', {})
    driver.execute_cdp_cmd('Network.setCacheDisabled', {'cacheDisabled': True})
    driver.refresh()
    page.wait.until(EC.visibility_of_element_located(page.ROWS))
    results['after_reload'] = page.titles()
    results['cache'] = driver.execute_async_script("const done=arguments[0]; fetch('/api/health').then(r => done({status:r.status, cacheControl:r.headers.get('Cache-Control')}))")
    (out / 'inspection.json').write_text(json.dumps(results, ensure_ascii=False, indent=2))
finally:
    driver.quit()
