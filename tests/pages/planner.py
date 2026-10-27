from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


class PlannerPage:
    EMAIL = (By.ID, 'email')
    PASSWORD = (By.ID, 'password')
    LOGIN = (By.ID, 'login-button')
    PANEL = (By.ID, 'tasks-panel')
    TITLE = (By.ID, 'title')
    ROWS = (By.CSS_SELECTOR, '#tasks .task')

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 8, poll_frequency=0.1)

    def open(self):
        self.driver.get(self.base_url)
        self.wait.until(EC.visibility_of_element_located(self.EMAIL))
        return self

    def login(self, email='student@example.com', password='Study123!'):
        for locator, value in ((self.EMAIL, email), (self.PASSWORD, password)):
            field = self.driver.find_element(*locator)
            field.clear()
            field.send_keys(value)
        self.wait.until(EC.element_to_be_clickable(self.LOGIN)).click()
        return self

    def ready(self):
        self.wait.until(EC.visibility_of_element_located(self.PANEL))
        self.wait.until(EC.text_to_be_present_in_element((By.ID, 'service-status'), 'Сервис доступен'))
        return self

    def add(self, title, priority='Обычный'):
        old_count = len(self.driver.find_elements(*self.ROWS))
        field = self.driver.find_element(*self.TITLE)
        field.clear()
        field.send_keys(title)
        Select(self.driver.find_element(By.ID, 'priority')).select_by_visible_text(priority)
        self.driver.find_element(By.ID, 'add-task').click()
        self.wait.until(lambda d: len(d.find_elements(*self.ROWS)) == old_count + 1)
        return self

    def titles(self):
        return [row.find_element(By.TAG_NAME, 'span').text for row in self.driver.find_elements(*self.ROWS)]

    def error(self):
        return self.wait.until(lambda d: d.find_element(By.ID, 'login-error').text)
