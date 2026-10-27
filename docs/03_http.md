# Практики 2–3. Клиент–сервер и HTTP

Браузер загружает HTML, CSS и JavaScript с Python-сервера. JavaScript отправляет JSON в API, сервер проверяет данные и возвращает JSON. Браузер обновляет список задач без полной перезагрузки. Сервер хранит сессии и задачи в памяти.

Схема: браузер → HTTP-запрос → `app/server.py` → проверка данных/сессии → HTTP-ответ → отображение в браузере.

В URL `http://127.0.0.1:8000/api/health`:

| Часть | Значение |
|---|---|
| Схема | `http` |
| Хост | `127.0.0.1`, loopback текущего компьютера |
| Порт | `8000` |
| Путь | `/api/health` |
| Query и fragment | Отсутствуют |

Пример структуры URL для разбора: `https://example.com:443/tasks?filter=open#list`. `filter=open` — query, `list` — fragment; fragment не отправляется серверу. Этот пример не является выполненным запросом.

## Обязательное задание №2

В Chrome Dev 158 открыта страница API, затем DevTools → Network. Страница перезагружена, выбран запрос `health`, просмотрены Headers и Response.

| Поле | Фактически наблюдалось |
|---|---|
| URL | `http://127.0.0.1:8000/api/health` |
| Метод | GET |
| Статус | 200 OK |
| Request headers | `Host: 127.0.0.1:8000`, `Accept: text/html,...`, `Accept-Encoding: gzip, deflate, br, zstd`, `Cache-Control: max-age=0` |
| Тело запроса | Отсутствует |
| Response headers | `Content-Type: application/json; charset=utf-8`, `Content-Length: 60`, `Cache-Control: no-store`, `Server: BaseHTTP/0.6 Python/3.14.7` |
| Тело ответа | `{"status": "ok", "message": "Сервис доступен"}` |

Снимки: [Headers](../evidence/screenshots/devtools-headers.png), [Response](../evidence/screenshots/devtools-response.png).
Дополнительно сохранены [машиночитаемые события Chrome DevTools Protocol](../evidence/http-devtools.json) для fetch того же API из приложения. Там `Accept: */*`, потому что запрос выполняет JavaScript, а не навигация браузера.

Проверенные коды приложения: 200 — успешный вход/чтение, 201 — задача создана, 400 — недопустимая длина, 401 — неверные данные или нет сессии, 404 — неизвестная страница. Они проверяются в `tests/test_api.py` и UI-тестах.
GET читает данные. POST в этом приложении выполняет вход, создание и изменение задач. PUT заменяет ресурс, PATCH частично изменяет, DELETE удаляет; последние три метода в учебном сервере не реализованы.

HTTP передаёт данные без шифрования. HTTPS добавляет TLS, проверку сертификата и защиту содержимого при передаче. Здесь проверялся только локальный HTTP: TLS и сертификаты не настроены. Учебные данные нельзя заменять реальными паролями.
