import sys
from pathlib import Path



import pytest
from app import create_app, DependencyContainer
from db import UserRepository, AccountRepository, TransactionRepository
from auth import AuthRepository
from datetime import timezone, datetime
from models import UserCredential, Account, Transaction

# Add the project root directory to Python's path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


@pytest.fixture()
def app():
    app =  create_app()
    app.config.update({
        "TESTING": True,
        "JWT_SECRET": "test"
    })

    yield app
    # do cleanup here

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

@pytest.fixture()
def test_user():
    return UserCredential(name="test_user", email="test@example.com", password="password")

@pytest.fixture()
def test_account():
    return Account(user_id="foo", balance=1000)

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
def app_with_test_user(test_user: UserCredential):
    ts = datetime.now(timezone.utc).isoformat()
    users = {"foo": {"id": "foo", "name": test_user.name, "email": test_user.email, "password": test_user.password, "updated_at": ts, "created_at":ts }}
    dependencies = DependencyContainer(users=UserRepository(users))
    app = create_app(dependencies=dependencies)

    app.config.update({
        "TESTING": True,
        "JWT_SECRET": "test"
    })

    yield app
    # cleanup here

@pytest.fixture()
def app_with_test_data(test_user: UserCredential, test_account: Account, test_transaction: Transaction):
    ts = datetime.now(timezone.utc).isoformat()
    users = {"foo": {"id": "foo", "name": test_user.name, "email": test_user.email, "password": test_user.password, "updated_at": ts, "created_at":ts }}
    accounts = {"acc123": {"id": "acc123", "user_id": "foo", "balance": test_account.balance, "updated_at": ts, "created_at": ts}}
    transactions = {"txn123": {"id": "txn123", "user_id": "foo", "account_id": "acc123", "transaction_type": "deposit", "amount": 500, "sender_account": None, "recipient_account": None, "created_at": ts}}

    auth = AuthRepository()
    auth.register(test_user.email, test_user.password, user_id="foo")
    
    dependencies = DependencyContainer(
        users=UserRepository(users),
        accounts=AccountRepository(accounts),
        transactions=TransactionRepository(transactions),
        auth=auth
    )
    
    app = create_app(dependencies=dependencies)

    app.config.update({
        "TESTING": True,
        "JWT_SECRET": "test"
    })

    yield app
    # cleanup here