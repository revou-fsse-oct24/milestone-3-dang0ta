from werkzeug.test import Client
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
import pytest
from app import create_app
from models import UserCredential, Account, Transaction
from db import Base, DB
from typing import List, Generator

@pytest.fixture()
def app() -> Generator[Flask, None, None]:
    app =  create_app()
    app.config.update()

    yield app
    Base.metadata.drop_all(DB.get_engine())


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()

@pytest.fixture()
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()

@pytest.fixture()
def test_user() -> UserCredential:
    return UserCredential(name="test_user", email_address="test@example.com", password="password")

@pytest.fixture()
def test_user_2() -> UserCredential:
    return UserCredential(name="test_user_2", email_address="test2@example.com", password="password")

@pytest.fixture()
def test_account() -> Account:
    return Account(balance=1000)

@pytest.fixture()
def test_account_2() -> Account:
    return Account(balance=1001)

@pytest.fixture()
def test_transaction():
    return Transaction(
        user_id="foo",
        account_id="acc123",
        transaction_type="deposit",
        amount=500,
        sender_account=None,
        recipient_account=None
    )

@pytest.fixture()
def access_token(client, test_user: UserCredential) -> str:
    response = client.post("/users/", json={"name": test_user.name, "email_address": test_user.email_address, "password": test_user.password})
    assert response.status_code == 201, response.get_data()

    response_data = response.get_json()
    assert response_data["id"] is not None

    response = client.post("/auth/login", json={"email": test_user.email_address, "password": test_user.password})
    assert response.status_code == 200, response.get_data()
    response_data = response.get_json()
    assert response_data["access_token"] is not None
    assert response_data["refresh_token"] is not None

    access_token = response_data["access_token"]
    return access_token

@pytest.fixture()
def access_token_2(client, test_user_2: UserCredential) -> str:
    response = client.post("/users/", json={"name": test_user_2.name, "email_address": test_user_2.email_address, "password": test_user_2.password})
    assert response.status_code == 201, response.get_data()

    response_data = response.get_json()
    assert response_data["id"] is not None

    response = client.post("/auth/login", json={"email": test_user_2.email_address, "password": test_user_2.password})
    assert response.status_code == 200, response.get_data()
    response_data = response.get_json()
    assert response_data["access_token"] is not None
    assert response_data["refresh_token"] is not None

    access_token = response_data["access_token"]
    return access_token

@pytest.fixture()
def test_user_with_accounts(client, access_token: str, test_account: Account) -> List[Account]:    
    response = client.post("/accounts/", headers={"Authorization": f"Bearer {access_token}"}, json={"balance": test_account.balance})
    assert response.status_code == 201, response.get_data()
    response_json = response.get_json()
    assert "account_id" in response_json
    return [test_account]

@pytest.fixture()
def test_user_with_account_id(client, access_token: str, test_account: Account) -> str:    
    response = client.post("/accounts/", headers={"Authorization": f"Bearer {access_token}"}, json={"balance": test_account.balance})
    assert response.status_code == 201, response.get_data()
    response_json = response.get_json()
    assert "account_id" in response_json
    return str(response_json["account_id"])

@pytest.fixture()
def account_id(client: Client, access_token: str, test_account: Account) -> str:
    response = client.post("/accounts/", headers={"Authorization": f"Bearer {access_token}"}, json={"balance": test_account.balance})
    assert response.status_code == 201, response.get_data()
    response_json = response.get_json()
    assert "account_id" in response_json
    return str(response_json["account_id"])

@pytest.fixture()
def account_id_2(client: Client, access_token_2: str, test_account_2: Account) -> str:
    response = client.post("/accounts/", headers={"Authorization": f"Bearer {access_token_2}"}, json={"balance": test_account_2.balance})
    assert response.status_code == 201, response.get_data()
    response_json = response.get_json()
    assert "account_id" in response_json
    return str(response_json["account_id"])

@pytest.fixture()
def test_user_with_transaction(client: Client, access_token: str, test_user_with_account_id: str) -> Transaction:
    response = client.post("/transactions/deposit", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 100, "account_id": test_user_with_account_id})
    assert response.status_code == 200, response.get_data()
    response_json = response.get_json()
    assert "transaction" in response_json
    return response_json["transaction"]


@pytest.fixture()
def deposit(client: Client, access_token: str, account_id: str) -> Transaction:
    response = client.post("/transactions/deposit", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 102, "account_id": account_id})
    assert response.status_code == 200, f"failed to deposit, status code is {response.status_code} {response.get_data()}"
    response_json = response.get_json()
    assert "transaction" in response_json, f"invalid deposit response, no key 'transaction' found, {response_json}"
    return Transaction(**response_json["transaction"])

@pytest.fixture()
def withdraw(client: Client, access_token: str, account_id) -> Transaction:
    response = client.post("/transactions/withdraw", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 101, "account_id": account_id})
    assert response.status_code == 200, f"failed to withdraw, status code is {response.status_code}"
    response_json = response.get_json()
    assert "transaction" in response_json, f"invalid withdraw response, no key 'transaction' found"
    return Transaction(**response_json["transaction"])

@pytest.fixture()
def transfer(client: Client, access_token: str, access_token_2: str, account_id: str, account_id_2: str) -> Transaction:
    response = client.post("/transactions/transfer", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 103, "account_id": account_id, "recipient_account_id": account_id_2})
    assert response.status_code == 200, f"failed to transfer, status code is {response.status_code}"
    response_json = response.get_json()
    assert "transaction" in response_json, f"invalid withdraw response, no key 'transaction' found"
    return Transaction(**response_json["transaction"])



