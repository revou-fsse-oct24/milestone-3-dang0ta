import sys
from pathlib import Path
import pytest
from app import create_app
from models import UserCredential, Account, Transaction
from db import Base, DB

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
def test_user():
    return UserCredential(name="test_user", email_address="test@example.com", password="password")

@pytest.fixture()
def test_account():
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