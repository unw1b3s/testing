import json
from http.cookiejar import CookieJar
from urllib.error import HTTPError
from urllib.request import Request, build_opener, HTTPCookieProcessor

import pytest


@pytest.fixture
def client(base_url):
    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    def send(path, data=None):
        request = Request(base_url + path, None if data is None else json.dumps(data).encode(), {'Content-Type': 'application/json'})
        try:
            response = opener.open(request)
        except HTTPError as error:
            response = error
        return response.code, json.load(response)
    return send


def login(client):
    assert client('/api/login', {'email': 'student@example.com', 'password': 'Study123!'})[0] == 200


def test_protected_api(client):
    assert client('/api/tasks')[0] == 401
    assert client('/missing')[0] == 404


@pytest.mark.parametrize('length,status', [(0, 400), (1, 201), (79, 201), (80, 201), (81, 400)])
def test_api_title_boundaries(client, length, status):
    login(client)
    actual, body = client('/api/tasks', {'title': 'Я' * length})
    assert actual == status
    if status == 201:
        assert body['title'] == 'Я' * length


def test_sessions_are_isolated(base_url, client):
    login(client)
    assert client('/api/tasks', {'title': 'Личная задача'})[0] == 201
    other = build_opener(HTTPCookieProcessor(CookieJar()))
    response = other.open(Request(base_url + '/api/login', json.dumps({'email': 'student@example.com', 'password': 'Study123!'}).encode(), {'Content-Type': 'application/json'}))
    assert response.code == 200
    assert json.load(other.open(base_url + '/api/tasks')) == {'tasks': []}
    assert len(client('/api/tasks')[1]['tasks']) == 1
    assert client('/api/logout', {})[0] == 200
    assert client('/api/tasks')[0] == 401
