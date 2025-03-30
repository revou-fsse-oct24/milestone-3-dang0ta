import sys
from pathlib import Path
import pytest
from app import create_app
from models import UserCredential, Account, Transaction
from db import Base, DB
from typing import List

@pytest.fixture()
def app():
    app =  create_app()
    app.config.update()

    yield app
    Base.metadata.drop_all(DB.get_engine())


@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

@pytest.fixture()
def test_user() -> UserCredential:
    return UserCredential(name="test_user", email_address="test@example.com", password="password")

@pytest.fixture()
def test_account() -> Account:
    return Account(balance=1000)

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
def access_token(client, test_user: UserCredential):
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
    return response_json["account_id"]