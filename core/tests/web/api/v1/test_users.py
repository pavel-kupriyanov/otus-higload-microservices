from fastapi.testclient import TestClient

from social_network.db.models import AccessToken

BASE_PATH = '/users/'


def test_get(app: TestClient, user1, user2, user3):
    response = app.get(f'{BASE_PATH}{user1.id}/')
    assert response.status_code == 200
    assert response.json()['first_name'] == user1.first_name


def test_get_not_found(app: TestClient):
    response = app.get(f'{BASE_PATH}100000/')
    assert response.status_code == 404


def test_list(app: TestClient, user1, user2, user3):
    response = app.get(BASE_PATH)
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_list_search(app: TestClient, user1, user2, user3):
    response = app.get(BASE_PATH, params={'first_name': user1.first_name[0:-2]})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['first_name'] == user1.first_name


def test_list_not_found(app: TestClient):
    response = app.get(BASE_PATH)
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_list_friend_id(app: TestClient, user1, user2, user3, friendship):
    response = app.get(BASE_PATH, params={'friends_of': user1.id})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['first_name'] == user2.first_name


def test_list_ids(app: TestClient, user1, user2, user3):
    response = app.get(BASE_PATH, params={'ids': [user1.id]})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['first_name'] == user1.first_name


def test_list_without_hobbies(app: TestClient, user1, user_hobby):
    response = app.get(BASE_PATH, params={'with_hobbies': False})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0].get('hobbies') == []


def test_list_paginate(app: TestClient, user1, user2, user3):
    response = app.get(BASE_PATH, params={'paginate_by': 1, 'page': 1})
    assert response.status_code == 200
    assert len(response.json()) == 1
    raw_user_1 = response.json()[0]
    response = app.get(BASE_PATH, params={'paginate_by': 1, 'page': 2})
    assert len(response.json()) == 1
    raw_user_2 = response.json()[0]
    assert raw_user_1['id'] != raw_user_2['id']


def test_user_add_hobby(app: TestClient, user1, token1: AccessToken, hobby):
    response = app.put(f'{BASE_PATH}hobbies/{hobby.id}/',
                       headers={'x-auth-token': token1.value})
    assert response.status_code == 201


def test_user_add_hobby_already_added(app: TestClient, user1,
                                      token1: AccessToken, hobby, user_hobby):
    response = app.put(f'{BASE_PATH}hobbies/{hobby.id}/',
                       headers={'x-auth-token': token1.value})
    assert response.status_code == 400


def test_user_add_hobby_not_found(app: TestClient, user1, token1: AccessToken,
                                  hobby):
    response = app.put(f'{BASE_PATH}hobbies/100000/',
                       headers={'x-auth-token': token1.value})
    assert response.status_code == 400


def test_user_delete_hobby(app: TestClient, user1,
                           token1: AccessToken, hobby, user_hobby):
    response = app.delete(f'{BASE_PATH}hobbies/{hobby.id}/',
                          headers={'x-auth-token': token1.value})
    assert response.status_code == 204


def test_user_with_hobby(app: TestClient, user1, user_hobby):
    response = app.get(f'{BASE_PATH}{user1.id}/')
    assert response.status_code == 200
    assert response.json()['first_name'] == user1.first_name


def test_users_with_hobby(app: TestClient, user1, user2, user_hobby):
    response = app.get(BASE_PATH)
    assert response.status_code == 200
    assert len(response.json()) == 2
    filtered = [u for u in response.json() if u.get("hobbies")]
    assert len(filtered) == 1
