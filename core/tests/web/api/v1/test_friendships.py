from fastapi.testclient import TestClient

from social_network.db.models import AccessToken, FriendRequest, Friendship

BASE_PATH = '/friendships/'


def test_create_non_authorized(app: TestClient):
    response = app.post(f'{BASE_PATH}1/',
                        headers={'x-auth-token': 'foobar'})
    assert response.status_code == 401


def test_create(app: TestClient, user1, user2, token1: AccessToken):
    response = app.post(f'{BASE_PATH}{user2.id}/',
                        headers={'x-auth-token': token1.value})
    assert response.status_code == 201


def test_create_not_found(app: TestClient, user1, token1: AccessToken):
    response = app.post(f'{BASE_PATH}100000/',
                        headers={'x-auth-token': token1.value})
    assert response.status_code == 404
    assert 'not found' in response.json()['detail']


def test_create_already_request(app: TestClient, user1, user2,
                                token1: AccessToken, friend_request):
    response = app.post(f'{BASE_PATH}{user2.id}/',
                        headers={'x-auth-token': token1.value})
    assert response.status_code == 404
    assert 'already' in response.json()['detail']


def test_create_already_friends(app: TestClient, user1, user2,
                                token1: AccessToken, friendship):
    response = app.post(f'{BASE_PATH}{user2.id}/',
                        headers={'x-auth-token': token1.value})
    assert response.status_code == 400
    assert 'already' in response.json()['detail']


def test_cancel(app: TestClient, token1: AccessToken,
                friend_request: FriendRequest):
    response = app.delete(f'{BASE_PATH}{friend_request.id}/',
                          headers={'x-auth-token': token1.value})
    assert response.status_code == 204


def test_cancel_not_found(app: TestClient, token1: AccessToken, friend_request):
    response = app.delete(f'{BASE_PATH}100000/',
                          headers={'x-auth-token': token1.value})
    assert response.status_code == 404


def test_cancel_forbidden(app: TestClient, token2: AccessToken,
                          friend_request: FriendRequest):
    response = app.delete(f'{BASE_PATH}{friend_request.id}/',
                          headers={'x-auth-token': token2.value})
    assert response.status_code == 403


def test_get(app: TestClient, token1: AccessToken,
             friend_request: FriendRequest):
    response = app.get(f'{BASE_PATH}{friend_request.id}/',
                       headers={'x-auth-token': token1.value})
    assert response.status_code == 200


def test_get_not_found(app: TestClient, token1: AccessToken, friend_request):
    response = app.get(f'{BASE_PATH}1000000/',
                       headers={'x-auth-token': token1.value})
    assert response.status_code == 404


def test_get_forbidden(app: TestClient, token3: AccessToken,
                       friend_request: FriendRequest):
    response = app.get(f'{BASE_PATH}{friend_request.id}/',
                       headers={'x-auth-token': token3.value})
    assert response.status_code == 403


def test_decline(app: TestClient, token2: AccessToken,
                 friend_request: FriendRequest):
    response = app.put(f'{BASE_PATH}decline/{friend_request.id}/',
                       headers={'x-auth-token': token2.value})
    assert response.status_code == 204
    response = app.get(f'{BASE_PATH}{friend_request.id}/',
                       headers={'x-auth-token': token2.value})
    assert response.json()['status'] == 'DECLINED'


def test_decline_not_found(app: TestClient, token1: AccessToken,
                           friend_request):
    response = app.put(f'{BASE_PATH}decline/100000000/',
                       headers={'x-auth-token': token1.value})
    assert response.status_code == 404


def test_decline_forbidden(app: TestClient, token3: AccessToken,
                           friend_request: FriendRequest):
    response = app.put(f'{BASE_PATH}decline/{friend_request.id}/',
                       headers={'x-auth-token': token3.value})
    assert response.status_code == 403


def test_accept(app: TestClient, token2: AccessToken,
                friend_request: FriendRequest):
    response = app.put(f'{BASE_PATH}accept/{friend_request.id}/',
                       headers={'x-auth-token': token2.value})
    assert response.status_code == 201
    assert response.json()['friend_id'] == friend_request.from_user
    assert response.json()['user_id'] == friend_request.to_user


def test_accept_not_found(app: TestClient, token1: AccessToken,
                          friend_request):
    response = app.put(f'{BASE_PATH}accept/10000000/',
                       headers={'x-auth-token': token1.value})
    assert response.status_code == 404


def test_accept_forbidden(app: TestClient, token3: AccessToken,
                          friend_request: FriendRequest):
    response = app.put(f'{BASE_PATH}accept/{friend_request.id}/',
                       headers={'x-auth-token': token3.value})
    assert response.status_code == 403


def test_list(app: TestClient, token1: AccessToken,
              friend_request: FriendRequest):
    response = app.get(f'{BASE_PATH}', headers={'x-auth-token': token1.value})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_delete(app: TestClient, token1: AccessToken, friendship: Friendship):
    response = app.delete(f'{BASE_PATH}friendship/{friendship.friend_id}/',
                          headers={'x-auth-token': token1.value})
    assert response.status_code == 204


def test_delete_not_authorized(app: TestClient, friendship: Friendship):
    response = app.delete(f'{BASE_PATH}friendship/{friendship.friend_id}/',
                          headers={'x-auth-token': 'foobar'})
    assert response.status_code == 401
