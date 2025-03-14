from werkzeug.test import Client
from auth_jwt.tokens import create_access_token
from models import UserInformation, UserCredential

def test_getting_unauthenticated_current_user(client):
    response = client.get("/users/me")
    assert response.status_code == 401

def test_getting_authenticated_current_user(client, app):
    # create access token requires app context to get JWT_SECRET from app.config
    with app.app_context():
        token = create_access_token(identity="foo")
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.get_data() == b'user not found'

def test_create_new_user(client: Client):
    response = client.post("/users/", json={"name": "foo", "email": "foo@bar.com", "password": "password"})
    assert response.status_code == 201, response.get_data()

def test_create_new_user_missing_name(client: Client):
    response = client.post("/users/", json={"email": "foo@bar.com", "password": "password"})
    assert response.status_code == 400, response.get_data()
    assert response.get_data() == b'{"error":"missing user name"}\n'

def test_create_new_user_missing_email(client: Client):
    response = client.post("/users/", json={"name": "foo", "password": "password"})
    assert response.status_code == 400, response.get_data()
    assert response.get_data() == b'{"error":"missing email"}\n'

def test_create_new_user_invalid_email(client: Client):
    response = client.post("/users/", json={"email": "foobarqux", "name": "foo", "password": "password"})
    assert response.status_code == 400, response.get_data()
    assert response.get_data() == b'{"error":"invalid email"}\n'

def test_create_new_user_missing_password(client: Client):
    response = client.post("/users/", json={"name": "foo", "email": "foo@bar.com"})
    assert response.status_code == 400, response.get_data()
    assert response.get_data() == b'{"error":"missing password"}\n'

def test_getting_authenticated_current_user_success(app_with_test_user, test_user, client: Client):
    client = app_with_test_user.test_client()
    with app_with_test_user.app_context():
        token = create_access_token(identity="foo")

    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data["name"] == test_user.name
    assert response_data["email"] == test_user.email

def test_update_current_user(app_with_test_user, client: Client):
    client = app_with_test_user.test_client()
    with app_with_test_user.app_context():
        token = create_access_token(identity="foo")
    response = client.put("/users/me", headers={"Authorization": f"Bearer {token}"}, json={"email": "foo@bar.qux", "name": "foo"})
    assert response.status_code == 200, response.get_data()
    response_data = response.get_json()
    assert response_data["name"] == "foo"
    assert response_data["email"] == "foo@bar.qux"
