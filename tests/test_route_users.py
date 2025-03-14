from werkzeug.test import Client
from auth_jwt.tokens import create_access_token
from db.users import create_user

def test_getting_unauthenticated_current_user(client):
    response = client.get("/users/me")
    assert response.status_code == 401

def test_getting_authenticated_current_user(client, app):
    # create access token requires app context to get JWT_SECRET from app.config
    with app.app_context():
        token = create_access_token(identity="foo")
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.get_json()["error"] == 'user not found'

def test_create_new_user(client: Client):
    response = client.post("/users/", json={"name": "foo", "email_address": "foo@bar.com", "password": "password"})
    assert response.status_code == 201, response.get_data()

def test_create_new_user_missing_name(client: Client):
    response = client.post("/users/", json={"email_address": "foo@bar.com", "password": "password"})
    assert response.status_code == 400, response.get_data()
    assert response.get_data() == b'{"error":"missing user name"}\n'

def test_create_new_user_missing_email(client: Client):
    response = client.post("/users/", json={"name": "foo", "password": "password"})
    assert response.status_code == 400, response.get_data()
    assert response.get_data() == b'{"error":"missing email address"}\n'

def test_create_new_user_invalid_email(client: Client):
    response = client.post("/users/", json={"email_address": "foobarqux", "name": "foo", "password": "password"})
    assert response.status_code == 400, response.get_data()
    assert response.get_data() == b'{"error":"invalid email address"}\n'

def test_create_new_user_missing_password(client: Client):
    response = client.post("/users/", json={"name": "foo", "email_address": "foo@bar.com"})
    assert response.status_code == 400, response.get_data()
    assert response.get_data() == b'{"error":"missing password"}\n'

def test_getting_authenticated_current_user_success(app, test_user, client: Client):
    id = create_user(test_user)

    with app.app_context():
        token = create_access_token(identity=id)
        response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.get_data()
        response_data = response.get_json()
        assert response_data["name"] == test_user.name
        assert response_data["email_address"] == test_user.email_address

def test_update_current_user(app, test_user, client: Client):
    id = create_user(test_user)
    with app.app_context():
        token = create_access_token(identity=id)

        response = client.put("/users/me", headers={"Authorization": f"Bearer {token}"}, json={"email_address": "foo@bar.qux", "name": "foo"})
        assert response.status_code == 200, response.get_data()
        response_data = response.get_json()
        assert response_data["name"] == "foo"
        assert response_data["email_address"] == "foo@bar.qux"
