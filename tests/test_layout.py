import pytest


@pytest.mark.parametrize('width,height', [(320, 568), (375, 812), (768, 1024), (1280, 720), (1920, 1080)])
def test_long_title_layout(page, driver, width, height):
    page.login().ready().add('Я' * 80)
    if hasattr(driver, 'execute_cdp_cmd'):
        driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {'width': width, 'height': height, 'deviceScaleFactor': 1, 'mobile': width < 600})
    else:
        driver.set_window_size(width, height)
    size = driver.execute_script('return {viewport: innerWidth, content: document.documentElement.scrollWidth}')
    assert size['content'] <= size['viewport'], size
