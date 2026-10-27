import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

pytestmark = pytest.mark.smoke


def test_open_login(page, driver):
    assert driver.title == 'Учебный планировщик'
    assert driver.find_element(By.ID, 'login-button').is_displayed()


def test_login_and_logout(page, driver):
    page.login().ready()
    assert driver.find_element(By.ID, 'empty').text == 'Задач пока нет'
    driver.find_element(By.ID, 'logout').click()
    page.wait.until(EC.visibility_of_element_located(page.EMAIL))
    driver.refresh()
    assert driver.find_element(By.ID, 'login-panel').is_displayed()


def test_create_task(page, driver):
    page.login().ready().add('Подготовить отчёт', 'Высокий')
    assert page.titles() == ['Подготовить отчёт']
    assert driver.find_element(By.CSS_SELECTOR, '.task small').text == 'Высокий'
    driver.refresh()
    page.wait.until(EC.visibility_of_element_located(page.ROWS))
    assert page.titles() == ['Подготовить отчёт']


def test_complete_and_delete(page, driver):
    page.login().ready().add('Прочитать конспект')
    driver.find_element(By.CSS_SELECTOR, '.task input').click()
    page.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.task.done')))
    driver.find_element(By.CSS_SELECTOR, 'input[value=open]').click()
    page.wait.until(lambda d: len(d.find_elements(*page.ROWS)) == 0)
    driver.find_element(By.CSS_SELECTOR, 'input[value=all]').click()
    driver.find_element(By.CSS_SELECTOR, '.task button').click()
    page.wait.until(EC.alert_is_present()).accept()
    page.wait.until(lambda d: len(d.find_elements(*page.ROWS)) == 0)
    assert driver.find_element(By.ID, 'empty').is_displayed()


def test_navigation(page, driver):
    driver.find_element(By.ID, 'about-link').click()
    page.wait.until(EC.title_is('О приложении'))
    assert 'Планировщик' in driver.find_element(By.TAG_NAME, 'main').text
    driver.find_element(By.ID, 'home-link').click()
    page.wait.until(EC.title_is('Учебный планировщик'))
