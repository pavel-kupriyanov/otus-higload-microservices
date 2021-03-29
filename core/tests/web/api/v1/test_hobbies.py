from fastapi.testclient import TestClient

from social_network.db.models import AccessToken, Hobby

BASE_PATH = '/hobbies/'


def test_create(app: TestClient, token1: AccessToken):
    response = app.post(BASE_PATH,
                        json={'name': 'fencing'},
                        headers={'x-auth-token': token1.value})
    assert response.status_code == 201
    assert response.json()['name'] == 'Fencing'


def test_create_already_exists(app: TestClient, token1: AccessToken,
                               hobby: Hobby):
    response = app.post(BASE_PATH,
                        json={'name': hobby.name},
                        headers={'x-auth-token': token1.value})
    assert response.status_code == 201
    assert response.json()['name'] == hobby.name


def test_hobbies_not_authorized(app: TestClient):
    response = app.post(BASE_PATH,
                        json={'name': 'fencing'},
                        headers={'x-auth-token': 'foobar'})
    assert response.status_code == 401


def test_get(app: TestClient, hobby: Hobby):
    response = app.get(f'{BASE_PATH}{hobby.id}/')
    assert response.status_code == 200
    assert response.json()['name'] == hobby.name


def test_get_not_found(app: TestClient, hobby: Hobby):
    response = app.get(f'{BASE_PATH}10000/')
    assert response.status_code == 404


def test_list(app: TestClient, hobby: Hobby):
    response = app.get(BASE_PATH)
    assert response.status_code == 200
    assert response.json()[0]['name'] == hobby.name


def test_list_search(app: TestClient, hobby: Hobby):
    response = app.get(BASE_PATH, params={'name': hobby.name[0:-2]})
    assert response.status_code == 200
    assert response.json()[0]['name'] == hobby.name


def test_list_not_found(app: TestClient, hobby: Hobby):
    response = app.get(BASE_PATH, params={'name': 'foobar'})
    assert response.status_code == 200
    assert len(response.json()) == 0
