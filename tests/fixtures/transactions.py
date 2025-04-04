from werkzeug.test import Client
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
import pytest
from app import create_app
from models import UserCredential, Account, Transaction
from db import Base, DB
from typing import List, Generator

@pytest.fixture
def deposit(client: Client, access_token: str, account_id: str) -> Transaction:
    response = client.post("/transactions/deposit", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 102, "account_id": account_id})
    assert response.status_code == 200, f"failed to deposit, status code is {response.status_code} {response.get_data()}"
    response_json = response.get_json()
    assert "transaction" in response_json, f"invalid deposit response, no key 'transaction' found, {response_json}"
    return Transaction(**response_json["transaction"])

@pytest.fixture
def withdraw(client: Client, access_token: str, account_id) -> Transaction:
    response = client.post("/transactions/withdraw", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 101, "account_id": account_id})
    assert response.status_code == 200, f"failed to withdraw, status code is {response.status_code}"
    response_json = response.get_json()
    assert "transaction" in response_json, f"invalid withdraw response, no key 'transaction' found"
    return Transaction(**response_json["transaction"])

@pytest.fixture
def transfer(client: Client, access_token: str, access_token_2: str, account_id: str, account_id_2: str) -> Transaction:
    response = client.post("/transactions/transfer", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 103, "account_id": account_id, "recipient_account_id": account_id_2})
    assert response.status_code == 200, f"failed to transfer, status code is {response.status_code}"
    response_json = response.get_json()
    assert "transaction" in response_json, f"invalid withdraw response, no key 'transaction' found"
    return Transaction(**response_json["transaction"])
