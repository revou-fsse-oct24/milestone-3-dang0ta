import sys
from pathlib import Path



import pytest
from app import create_app, DependencyContainer
from db import UserRepository, AccountRepository, TransactionRepository
from auth import AuthRepository
from datetime import timezone, datetime
from models import UserCredential

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