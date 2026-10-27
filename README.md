# Тестирование информационных систем

Практические работы по МДК.05.03, индивидуальный график. Объект — собственное учебное приложение «Учебный планировщик».

[Требования и карта работ](docs/00_requirements.md) · [Результаты запусков](docs/09_results.md) · [GitHub Actions](https://github.com/unw1b3s/testing/actions)

## Работы

1. [Чек-лист, 5 тест-кейсов, тест-сьют](docs/01_test_documentation.md), [найденные дефекты и исправления](docs/02_bugs.md).
2. [Клиент–сервер, URL, HTTP/HTTPS и DevTools](docs/03_http.md).
3. [UI, макет и тестирование формы входа](docs/04_ui_forms.md).
4. [Матрица ОС и браузеров](docs/05_platforms.md).
5. [Адаптивность на пяти разрешениях и кэш](docs/06_layout_cache.md).
6. [Charles, Rewrite, Map Local, классы эквивалентности и границы](docs/07_charles_design.md).
7. [Selenium с POM и явными ожиданиями, Puppeteer, Grid](docs/08_automation.md).
8. [Пять смоук-тестов своего приложения и фактический CI](docs/09_results.md).
9. [Виды тестирования и план регрессии](docs/10_regression_plan.md).

## Приложение

Python 3.12+; для запуска приложения дополнительных библиотек не нужно.

```sh
python3 app/server.py
```

Открыть `http://127.0.0.1:8000/`. Учебный вход: `student@example.com` / `Study123!`.
Можно создавать задачи (1–80 символов), выбирать приоритет, отмечать выполнение, фильтровать и удалять. Данные хранятся в памяти текущего процесса и отдельно для каждой сессии; выход удаляет сессию. Регистрации и постоянного хранения нет. Это локальное учебное приложение, не готовый публичный сервис.

## Тесты

Нужен установленный Chrome; Selenium Manager загружает подходящий драйвер при первом запуске.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -v --junitxml=artifacts/results.xml
.venv/bin/python -m pytest -m smoke -v
```

pytest сам запускает сервер на свободном порту. Для Firefox: `BROWSER=firefox .venv/bin/python -m pytest -v`. При падении PNG и HTML сохраняются в `artifacts/`. Зависимости: Selenium и pytest.

Для Puppeteer нужны Node.js 22+ и отдельный запущенный сервер:

```sh
npm ci
npm run test:puppeteer
```

На macOS используется обычный путь Chrome, на другой ОС задать `CHROME_BINARY`. Подробности и Grid — в [инструкции](docs/08_automation.md).

## Доказательства и ограничения

`evidence/` содержит настоящие журналы, JUnit, ответы HTTP и снимки; исходные неуспешные прогоны сохранены отдельно. Успешный CI проверил 29 тестов в Chrome и 29 в Firefox, плюс Puppeteer.

Эмуляция размеров не заменяет реальные Android/iOS. Полный набор на Windows/Safari не выполнялся. Вместо сеанса Figma/Zeplin подготовлена локальная SVG-схема. Дополнительные ограничения Charles указаны в соответствующем отчёте.
