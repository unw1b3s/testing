# Практики 11–14. Charles и проектирование тестов

Объект: локальный `http://127.0.0.1:8000/api/health`. Charles 5.2.2, пробная версия, отдельный прокси `127.0.0.1:8899`. TLS-перехват не нужен: приложение использует HTTP. Системный прокси после первого запуска отключён; тестовые браузеры явно настроены на отдельный Charles. Веб-интерфейс управления не использовался.

## Перехват и подмена

Обычный ответ: `{"status":"ok","message":"Сервис доступен"}`. Сообщение отображается под списком задач после входа.

| Способ | Настройка | Фактический результат |
|---|---|---|
| Перехват | Запрос через прокси Charles | Получен HTTP 200 и исходный JSON: [ответ](../evidence/local/charles-original.json), [заголовки](../evidence/local/charles-original-headers.txt) |
| Rewrite, практика 12 | Body, только Response, заменить «Сервис доступен» на «Технические работы (Rewrite)», только точный health URL | PASS: [ответ](../evidence/charles/rewrite.json), [ОР/ФР](../evidence/charles/rewrite-ui.json), [снимок приложения](../evidence/charles/rewrite.png) |
| Map Local, практика 13 | Подставить `tools/charles/health.json` для того же URL | PASS: [ответ](../evidence/charles/map-local.json), [ОР/ФР](../evidence/charles/map-local-ui.json), [снимок](../evidence/charles/map-local.png) |

Оба режима выполнялись по отдельности настоящим Charles. Приложение не изменялось для подмены. `scripts/check_proxy.py` запускает отдельный Chrome через прокси, входит и сравнивает сообщение интерфейса с ожидаемым. Результаты относятся к отображению изменённого сообщения; блокировка действий при технических работах в требования приложения не входит.

Для повторения: запустить приложение и Charles; отключить macOS Proxy; установить HTTP-порт 8899; через Tools → Import/Export Settings импортировать настройки из `tools/charles`. В `map-local.xml` заменить `HEALTH_FILE_PATH` абсолютным путём к `health.json` или выбрать файл в Map Local. Для отдельного тестового Chrome отключить обход loopback: параметры `--proxy-server=http://127.0.0.1:8899` и `--proxy-bypass-list=<-loopback>`. Затем `python3 scripts/check_proxy.py rewrite` или `map-local`.

## Ручное изменение ответа, практика 11

Подготовлен breakpoint только Response для точного health URL: [настройка](../tools/charles/breakpoints.xml). Порядок проверки: отключить Rewrite и Map Local; включить breakpoint; отправить запрос; в Breakpoints → Edit Response → JSON/Text изменить `message` на «Технические работы (вручную)»; нажать Execute; проверить сообщение в приложении.

Проверка выполнена 27.10.2026: ответ остановлен в Breakpoints, текст JSON изменён в Edit Response → Text, после Execute приложение показало «Технические работы (вручную)». Фактический текст совпал с ожидаемым, PASS. Доказательства: [редактор перехваченного ответа](../evidence/charles/breakpoint-editor.png), [результат в приложении](../evidence/charles/breakpoint.png), [ОР/ФР и время](../evidence/charles/breakpoint-ui.json). Это отдельная ручная операция в графическом Charles; Rewrite и Map Local при ней отключены.

## Классы эквивалентности и границы, практика 14

Требование названия задачи: после `strip()` длина 1–80 символов. Классы: пустое/пробельное — недопустимо; 1–80 — допустимо; 81 и более — недопустимо. Unicode считается в символах Python, а не в байтах UTF-8; проверки выполнены на кириллице.

| Кейс | Данные и шаг | ОР | ФР |
|---|---|---|---|
| BV-01 | Войти; POST `/api/tasks`, `title=''` | 400 | PASS |
| BV-02 | Новый вход; название `Я` | 201, точный текст | PASS API и UI |
| BV-03 | Новый вход; 79 букв `Я` | 201, без обрезания | PASS API и UI |
| BV-04 | Новый вход; 80 букв `Я` | 201, без обрезания | PASS API и UI |
| BV-05 | Новый вход; POST с 81 буквой `Я` | 400 | PASS API |
| EQ-01 | Войти; ввести три пробела в UI; Добавить | Ошибка 1–80, задача не добавлена | PASS |
| EQ-02 | Войти; название `<b>Конспект</b>` | Буквальный текст, без HTML-элемента | PASS |

81 символ проверяется напрямую через API, поскольку поле UI ограничено `maxlength=80`. Доказательства: `test_api_title_boundaries`, `test_title_boundaries`, `test_spaces_title`, `test_text_is_not_html` в [JUnit](../evidence/local/pytest.xml).

Классы авторизации: существующая пара, неизвестная почта, неверный пароль, пустые поля и неверный формат. Для пароля UI нижняя граница 8: 7 символов блокируются, 9-символьный правильный пароль проходит. Проверки 8, 64 и 65 символов остаются дополнительными проектными случаями, их результаты не заявлены.

Источники: [Breakpoints](https://www.charlesproxy.com/documentation/proxying/breakpoints/), [Rewrite](https://www.charlesproxy.com/documentation/tools/rewrite/), [Map Local](https://www.charlesproxy.com/documentation/tools/map-local/).
