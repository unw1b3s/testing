import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.parametrize('email,password', [('other@example.com', 'Study123!'), ('student@example.com', 'Wrong123!')])
def test_wrong_credentials(page, driver, email, password):
    page.login(email, password)
    assert page.error() == 'Неверная почта или пароль'
    assert not driver.find_element(*page.PANEL).is_displayed()


@pytest.mark.parametrize('email,password,field,reason', [
    ('', 'Study123!', 'email', 'valueMissing'),
    ('student@example.com', '', 'password', 'valueMissing'),
    ('not-email', 'Study123!', 'email', 'typeMismatch'),
    ('student@example.com', '1234567', 'password', 'tooShort'),
])
def test_login_validation(page, driver, email, password, field, reason):
    page.login(email, password)
    assert driver.execute_script('return arguments[0].validity[arguments[1]]', driver.find_element(By.ID, field), reason)
    assert not driver.find_element(*page.PANEL).is_displayed()


@pytest.mark.parametrize('length', [1, 79, 80])
def test_title_boundaries(page, length):
    title = 'Я' * length
    page.login().ready().add(title)
    assert page.titles() == [title]


def test_spaces_title(page, driver):
    page.login().ready()
    driver.find_element(*page.TITLE).send_keys('   ')
    driver.find_element(By.ID, 'add-task').click()
    assert page.wait.until(lambda d: d.find_element(By.ID, 'task-error').text) == 'Название: от 1 до 80 символов'
    assert page.titles() == []


def test_text_is_not_html(page, driver):
    text = '<b>Конспект</b>'
    page.login().ready().add(text)
    assert page.titles() == [text]
    assert not driver.find_elements(By.CSS_SELECTOR, '.task b')


def test_frame_and_new_window(page, driver):
    driver.find_element(By.ID, 'about-link').click()
    page.wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'help-frame')))
    assert driver.find_element(By.ID, 'help-title').text == 'Справка'
    driver.switch_to.default_content()
    first = driver.current_window_handle
    driver.find_element(By.ID, 'help-link').click()
    page.wait.until(EC.number_of_windows_to_be(2))
    driver.switch_to.window(next(h for h in driver.window_handles if h != first))
    page.wait.until(EC.title_is('Справка'))
    assert driver.find_element(By.ID, 'help-title').text == 'Справка'
    driver.close()
    driver.switch_to.window(first)
