"""Учебный планировщик. Данные хранятся в памяти до остановки сервера."""
import argparse
import json
import secrets
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock

STATIC = Path(__file__).parent / 'static'
SESSIONS = {}
LOCK = Lock()
EMAIL = 'student@example.com'
PASSWORD = 'Study123!'


class Handler(BaseHTTPRequestHandler):
    def send(self, status, data, cookie=None):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        if cookie:
            self.send_header('Set-Cookie', cookie)
        self.end_headers()
        self.wfile.write(body)

    def session(self):
        cookie = SimpleCookie(self.headers.get('Cookie', ''))
        token = cookie.get('session')
        return SESSIONS.get(token.value) if token else None

    def do_GET(self):
        if self.path == '/api/health':
            return self.send(200, {'status': 'ok', 'message': 'Сервис доступен'})
        if self.path == '/api/tasks':
            with LOCK:
                session = self.session()
                return self.send(200, {'tasks': session['tasks']}) if session is not None else self.send(401, {'error': 'Требуется вход'})
        files = {'/': 'index.html', '/about': 'about.html', '/help': 'help.html', '/style.css': 'style.css', '/app.js': 'app.js'}
        name = files.get(self.path)
        if not name:
            return self.send(404, {'error': 'Страница не найдена'})
        body = (STATIC / name).read_bytes()
        types = {'.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript'}
        self.send_response(200)
        self.send_header('Content-Type', types[Path(name).suffix] + '; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            if length > 4096:
                return self.send(413, {'error': 'Слишком большой запрос'})
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError()
        except (ValueError, TypeError):
            return self.send(400, {'error': 'Неверный JSON'})
        with LOCK:
            if self.path == '/api/login':
                if data.get('email') != EMAIL or data.get('password') != PASSWORD:
                    return self.send(401, {'error': 'Неверная почта или пароль'})
                token = secrets.token_urlsafe(24)
                SESSIONS[token] = {'tasks': []}
                return self.send(200, {'email': EMAIL}, f'session={token}; HttpOnly; SameSite=Lax; Path=/')
            if self.path == '/api/logout':
                cookie = SimpleCookie(self.headers.get('Cookie', ''))
                if cookie.get('session'):
                    SESSIONS.pop(cookie['session'].value, None)
                return self.send(200, {'ok': True}, 'session=; Max-Age=0; Path=/; HttpOnly; SameSite=Lax')
            session = self.session()
            if session is None:
                return self.send(401, {'error': 'Требуется вход'})
            if self.path == '/api/tasks':
                title = data.get('title')
                if not isinstance(title, str) or not 1 <= len(title.strip()) <= 80:
                    return self.send(400, {'error': 'Название: от 1 до 80 символов'})
                priority = data.get('priority', 'Обычный')
                if priority not in ('Обычный', 'Высокий'):
                    return self.send(400, {'error': 'Неверный приоритет'})
                task = {'id': secrets.token_hex(4), 'title': title.strip(), 'priority': priority, 'done': False}
                session['tasks'].append(task)
                return self.send(201, task)
            for task in session['tasks']:
                if self.path == f"/api/tasks/{task['id']}/toggle":
                    task['done'] = not task['done']
                    return self.send(200, task)
                if self.path == f"/api/tasks/{task['id']}/delete":
                    session['tasks'].remove(task)
                    return self.send(200, {'ok': True})
            return self.send(404, {'error': 'Не найдено'})


def create_server(host='127.0.0.1', port=8000):
    return ThreadingHTTPServer((host, port), Handler)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    print(f'http://{args.host}:{args.port}', flush=True)
    create_server(args.host, args.port).serve_forever()
