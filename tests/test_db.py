import pytest
import bcrypt
from models import UserCredential
from db.users import create_user, get_user
from db.credentials import get_hash

@pytest.fixture
def sample_user():
    return UserCredential(name="foo", email_address="foo@gmail.com", password="foobarqux")

def test_create_get(sample_user):
    id = create_user(sample_user)
    hash = get_hash(email_address=sample_user.email_address)
    ok = bcrypt.checkpw(sample_user.password.encode(), hashed_password=hash)
    assert ok == True, "password doesn't match"
    user =get_user(id)
    assert user.email_address == sample_user.email_address
    assert user.name == sample_user.name
    assert user.fullname == sample_user.fullname
