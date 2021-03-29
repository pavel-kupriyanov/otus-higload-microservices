from fastapi.testclient import TestClient

BASE_PATH = '/auth/'


def test_login(app: TestClient, user1):
    request = {
        'email': user1.email,
        'password': user1.password
    }
    response = app.post(BASE_PATH + 'login', json=request)
    assert response.status_code == 201
    assert 'expired_at' in response.json().keys()


def test_login_invalid_payload(app: TestClient):
    response = app.post(BASE_PATH + 'login', {'foo': 'bar'})
    assert response.status_code == 422


def test_login_invalid_password(app: TestClient, user1):
    request = {
        'email': user1.email,
        'password': 'foobarfoobar'
    }
    response = app.post(BASE_PATH + 'login', json=request)
    assert response.status_code == 400


def test_register(app: TestClient, clear_users_after):
    request = {
        "email": 'KwisatzHaderach@mail.com',
        "password": 'death_for_atreides!',
        "first_name": 'Paul',
        "last_name": 'Atreides',
        "age": 16,
        "city": "Tabr"

    }
    response = app.post(BASE_PATH + 'register', json=request)
    assert response.status_code == 201


def test_register_invalid_payload(app: TestClient, clear_users_after):
    request = {
        "email": 'Harkonnen.v@mail.com',
        "password": 'death_for_atreides!',
    }
    response = app.post(BASE_PATH + 'register', json=request)
    assert response.status_code == 422


def test_register_email_already_exists(app: TestClient, user1,
                                       clear_users_after):
    request = {
        "email": 'Harkonnen.v@mail.com',
        "password": 'death_for_atreides!',
    }
    response = app.post(BASE_PATH + 'register', json=request)
    assert response.status_code == 422
