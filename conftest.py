from werkzeug.test import Client
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
import pytest
from app import create_app
from models import UserCredential, Account, Transaction
from db import Base, DB
from typing import List, Generator
from auth_jwt.blacklist import blacklisted_tokens

@pytest.fixture(autouse=True)
def clear_blacklist():
    blacklisted_tokens.clear()

@pytest.fixture
def app() -> Generator[Flask, None, None]:
    app =  create_app()
    app.config.update()

    yield app
    Base.metadata.drop_all(DB.get_engine())


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()

@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()

@pytest.fixture
def test_user() -> UserCredential:
    return UserCredential(name="test_user", email_address="test@example.com", password="password")

@pytest.fixture
def test_user_2() -> UserCredential:
    return UserCredential(name="test_user_2", email_address="test2@example.com", password="password")

@pytest.fixture
def admin() -> UserCredential:
    return UserCredential(name="admin", email_address="admin@example.com", password="changeme", roles=["admin", "customer"])

def create_access_token(client: FlaskClient, credential: UserCredential) -> str:
    response = client.post("/users/", json={"name": credential.name, "email_address": credential.email_address, "password": credential.password})
    assert response.status_code == 201, response.get_data()

    response_data = response.get_json()
    assert response_data["id"] is not None

    response = client.post("/auth/login", json={"email": credential.email_address, "password": credential.password})
    assert response.status_code == 200, response.get_data()
    response_data = response.get_json()
    assert response_data["access_token"] is not None
    assert response_data["refresh_token"] is not None

    access_token = response_data["access_token"]
    return access_token

@pytest.fixture
def admin_access_token(client: FlaskClient, admin: UserCredential) -> str:
    response = client.post("/users/", json={"name": admin.name, "email_address": admin.email_address, "password": admin.password, "roles": admin.roles})
    assert response.status_code == 201, response.get_data()

    response_data = response.get_json()
    assert response_data["id"] is not None

    response = client.post("/auth/login", json={"email": admin.email_address, "password": admin.password})
    assert response.status_code == 200, response.get_data()
    response_data = response.get_json()
    assert response_data["access_token"] is not None
    assert response_data["refresh_token"] is not None

    access_token = response_data["access_token"]
    return access_token

@pytest.fixture
def access_token(client, test_user: UserCredential) -> str:
    return create_access_token(client, test_user)

@pytest.fixture
def access_token_2(client, test_user_2: UserCredential) -> str:
    return create_access_token(client, test_user_2)


def create_account(client: FlaskClient, access_token: str, balance: int) -> Account:
    response = client.post("/accounts/", headers={"Authorization": f"Bearer {access_token}"}, json={"balance": balance})
    assert response.status_code == 201, response.get_data()
    response_json = response.get_json()
    assert "account" in response_json
    return Account(**response_json["account"])

@pytest.fixture
def account_1_1(client, access_token: str) -> Account:    
    return create_account(client, access_token, 1000)

@pytest.fixture
def account_1_2(client, access_token: str) -> Account:    
    return create_account(client, access_token, 1002)

@pytest.fixture
def account_2_1(client, access_token_2: str) -> Account:    
    return create_account(client, access_token_2, 1003)

@pytest.fixture
def account_2_2(client, access_token_2: str) -> Account:    
    return create_account(client, access_token_2, 1004)

def create_account_id(client: FlaskClient, access_token: str, balance: int)-> str:
    response = client.post("/accounts/", headers={"Authorization": f"Bearer {access_token}"}, json={"balance": balance})
    assert response.status_code == 201, response.get_data()
    response_json = response.get_json()
    assert "account" in response_json
    account = Account(**response_json["account"])
    return account.id

@pytest.fixture
def account_id(client: Client, access_token: str) -> str:
    return create_account_id(client, access_token, 1000)

@pytest.fixture
def account_id_2(client: Client, access_token_2: str) -> str:
    return create_account_id(client, access_token_2, 1001)

@pytest.fixture
def admin_account_id(client: Client, admin_access_token: str) -> str:
    return create_account_id(client, admin_access_token, 1003)