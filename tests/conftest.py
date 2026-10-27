import json
import os
import platform
import threading
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from app.server import create_server
from tests.pages.planner import PlannerPage

ARTIFACTS = Path(os.environ.get('ARTIFACT_DIR', 'artifacts'))


@pytest.fixture(scope='session')
def base_url():
    external = os.environ.get('BASE_URL')
    if external:
        yield external.rstrip('/')
        return
    server = create_server(port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_port}'
    server.shutdown()
    server.server_close()
    thread.join()


@pytest.fixture
def driver(request):
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    browser = os.environ.get('BROWSER', 'chrome')
    if browser == 'firefox':
        options = webdriver.FirefoxOptions()
        options.add_argument('-headless')
        instance = webdriver.Firefox(options=options)
    else:
        options = webdriver.ChromeOptions()
        if os.environ.get('CHROME_BINARY'):
            options.binary_location = os.environ['CHROME_BINARY']
        if os.environ.get('HEADED') != '1':
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL', 'browser': 'ALL'})
        if os.environ.get('SELENIUM_REMOTE_URL'):
            instance = webdriver.Remote(command_executor=os.environ['SELENIUM_REMOTE_URL'], options=options)
        else:
            instance = webdriver.Chrome(options=options, service=Service(log_output=str(ARTIFACTS / 'chromedriver.log')))
    instance.set_window_size(1280, 900)
    metadata = {'os': platform.platform(), 'python': platform.python_version(), 'capabilities': instance.capabilities}
    (ARTIFACTS / 'environment.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
    yield instance
    if hasattr(request.node, 'call_report') and request.node.call_report.failed:
        instance.save_screenshot(str(ARTIFACTS / f'{request.node.name}-failed.png'))
        (ARTIFACTS / f'{request.node.name}-page.html').write_text(instance.page_source)
    instance.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    if call.when == 'call':
        item.call_report = outcome.get_result()


@pytest.fixture
def page(driver, base_url):
    return PlannerPage(driver, base_url).open()
