import pytest
from app import create_app
from db import UserRepository, AccountRepository, TransactionRepository
from auth import AuthRepository
from werkzeug.test import Client

@pytest.fixture()
def app():
    app =  create_app(users=UserRepository({}), auth=AuthRepository(), accounts=AccountRepository({}), transactions=TransactionRepository({}))
    app.config.update({
        "TESTING": True
    })

    yield app
    # do cleanup here

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_getting_unauthenticated_current_user(client):
    response = client.get("/users/me")
    assert response.status_code == 401

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