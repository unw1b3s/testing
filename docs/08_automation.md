# Практики 15–17 и 17.1–17.10. Автоматизация

Автоматизированы повторяемые сценарии с понятным ОР: вход, работа с задачами, валидация, навигация, границы API и ширина страницы. Внешний вид и новые нестандартные сценарии дополнительно просматриваются по снимкам. Небольшую разовую визуальную проверку не всегда выгодно автоматизировать.

## Установка и запуск

Нужны Python 3.12+ и установленный Chrome. Для Firefox — установленный Firefox. Selenium Manager подбирает и загружает драйвер; для первого запуска нужен интернет. Зависимости Python закреплены в `requirements.txt`, npm — в `package-lock.json`.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -v --junitxml=artifacts/results.xml
.venv/bin/python -m pytest -m smoke -v
BROWSER=firefox .venv/bin/python -m pytest -v
```

Фикстура сама запускает настоящий HTTP-сервер на свободном порту, затем останавливает его. Внешний экземпляр можно указать через `BASE_URL`. `CHROME_BINARY` задаёт путь к нестандартному Chrome, `ARTIFACT_DIR` — папку результатов, `HEADED=1` отключает headless. Для воспроизведения снимков отдельно запустить `python3 app/server.py`, затем `python3 scripts/collect_evidence.py` в окружении с Selenium.

Selenium IDE записывает действия в браузере; WebDriver управляет настоящим браузером через драйвер. В работе использован Python WebDriver с pytest; Selenium IDE отдельно не использовалась. ChromeDriver обслуживает Chrome, GeckoDriver — Firefox. Версии браузеров и возможностей сохранены в `evidence/local/environment.json` и `evidence/ci/*/environment.json`.

## Локаторы

| Способ | Пример на странице |
|---|---|
| ID | `By.ID, 'email'` |
| name | `By.NAME, 'password'` |
| class | `By.CLASS_NAME, 'task'` после создания задачи |
| tag | `By.TAG_NAME, 'main'` |
| linkText | `By.LINK_TEXT, 'О приложении'` |
| partialLinkText | `By.PARTIAL_LINK_TEXT, 'приложении'` |
| CSS | `By.CSS_SELECTOR, '#tasks .task'` |
| XPath | `By.XPATH, "//input[@id='email']"` |

Таблица показывает варианты локаторов; в запускаемом наборе в основном применены ID и CSS. ID выбран для устойчивых отдельных элементов, CSS — для строк списка и состояний. Абсолютные XPath и позиции элементов не используются.

## Обязательное задание №4

`tests/pages/planner.py` — Page Object: хранит локаторы и действия `open`, `login`, `ready`, `add`. Проверки результата находятся в тестах. Авторизацию проверяют успешный сценарий в `test_smoke.py` и параметризованные негативные сценарии в `test_regression.py`.

Явные ожидания: `WebDriverWait`, `visibility_of_element_located`, `element_to_be_clickable`, `text_to_be_present_in_element`; для динамического списка — ожидание изменения числа строк. В POM интервал опроса 0.1 с, предел 8 с. Неявное ожидание оставлено равным нулю; `sleep` для синхронизации тестов не применяется. Fluent Wait обозначает настраиваемое ожидание с опросом и обработкой исключений; в Python такую настройку даёт `WebDriverWait`. Смешивать большие implicit и explicit ожидания не нужно.

Операции: ввод и очистка через `send_keys`/`clear`, клик по кнопке, `Select.select_by_visible_text`, флажок выполнения, радиофильтр. Подтверждение удаления обрабатывается через `alert_is_present().accept()`. В `test_frame_and_new_window` выполняются переключения в iframe, обратно в основной документ, в новую вкладку и обратно.

В `tests/conftest.py` hook `pytest_runtest_makereport` сохраняет результат теста. При фактическом падении фикстура делает PNG и сохраняет HTML, затем закрывает браузер. Эта ветка реально сработала при BUG-01: [скриншот](../evidence/bugs/BUG-01/login-failed.png), [исходный JUnit](../evidence/local/pytest-initial.xml). Логи и JUnit заменяют отдельный Allure; Allure не устанавливался.

## Puppeteer

Использован `puppeteer-core`, чтобы работать с уже установленным Chrome без второй загрузки браузера. Node.js импортирует библиотеку как ES-модуль. Тест открывает страницу, находит поля по ID, вводит данные, нажимает кнопку, сравнивает заголовок с «Мои задачи», добавляет задачу и сравнивает её текст через `assert.equal`.

```sh
npm ci
python3 app/server.py
# Во втором терминале:
npm run test:puppeteer
```

На Linux задать `CHROME_BINARY=/usr/bin/google-chrome`. `BASE_URL` по умолчанию `http://127.0.0.1:8000`.
Реальный результат: [локальный журнал](../evidence/local/puppeteer.txt), [снимок](../evidence/screenshots/puppeteer.png), [журнал CI](../evidence/ci/puppeteer.log).

## Selenium Grid и параллельный запуск

Локально запущен Selenium Server 4.51.0 в режиме standalone с Java 21 и двумя слотами Chrome. Это одна машина и два браузерных клиента, а не ферма из разных ОС.

```sh
java -Dwebdriver.chrome.driver=/путь/к/chromedriver -jar selenium-server-4.51.0.jar standalone --host 127.0.0.1 --port 4444 --max-sessions 2
python3 scripts/grid_smoke.py
```

`grid_smoke.py` одновременно запускает два Remote WebDriver через `ThreadPoolExecutor`. Каждый входит, создаёт свою задачу и проверяет собственный список. Два разных session ID и два PASS записаны в [grid-results.json](../evidence/local/grid-results.json); серверный журнал — [grid-server.txt](../evidence/local/grid-server.txt). Распределённый Grid на разных ОС не запускался.
