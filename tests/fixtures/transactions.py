from werkzeug.test import Client
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
import pytest
from app import create_app
from models import UserCredential, Account, Transaction
from db import Base, DB, db_session, Transactions as TransactionDB, TransactionEntries, TransactionCategories
from typing import List, Generator
from datetime import datetime,timezone, timedelta

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

@pytest.fixture
def transactions(client: Client, access_token:str, account_id: str) -> List[Transaction]:
    now = datetime.now(tz=timezone.utc)
    last_week, yesterday = now - timedelta(days=7), now - timedelta(days=1)

    transactions = [
        TransactionDB(
            transaction_type="withdraw",
            timestamp=last_week,
        ),
        TransactionDB(
            transaction_type="withdraw",
            timestamp=yesterday,
        ),
        TransactionDB(
            transaction_type="withdraw",
            timestamp=now,
        ),
    ]

    db_session.add_all(transactions)
    db_session.flush()

    transaction_entries = [
        TransactionEntries(
            amount=100,
            transaction_id=transactions[0].id,
            account_id=account_id,
            entry_type="debit"
        ),
        TransactionEntries(
            amount=100,
            transaction_id=transactions[1].id,
            account_id=account_id,
            entry_type="debit"
        ),
        TransactionEntries(
            amount=100,
            transaction_id=transactions[2].id,
            account_id=account_id,
            entry_type="debit"
        )
    ]

    categories = [
        TransactionCategories(
            name="test",
            transaction_id=transactions[0].id
        ),
        TransactionCategories(
            name="test",
            transaction_id=transactions[1].id
        ),
        TransactionCategories(
            name="test",
            transaction_id=transactions[2].id
        )
    ]

    db_session.add_all(transaction_entries)
    db_session.add_all(categories)
    db_session.flush()
    db_session.commit()

    transaction_models = []
    for i in range(len(transactions)):
        transaction_models.append(Transaction(
            id=str(transactions[i].id),
            account_id=str(account_id),
            category="test",
            transaction_type=transactions[i].transaction_type,
            amount=transaction_entries[i].amount,
            timestamp=transactions[i].timestamp.isoformat(),
        ))
    return transaction_models