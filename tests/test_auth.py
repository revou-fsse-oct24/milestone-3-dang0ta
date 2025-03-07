import pytest
from auth import AuthRepository, WrongCredentialException, UserNotFoundException

def test_authenticate():
    auth  = AuthRepository()
    auth.register(email="foo@bar.com", user_id="foo", password="test")
    
    assert auth.authenticate("foo@bar.com", "test") == "foo"

def test_authenticate_wrong_credential():
    auth  = AuthRepository()
    auth.register(email="foo@bar.com", user_id="foo", password="test")

    with pytest.raises(WrongCredentialException) as exc:
        auth.authenticate("foo@bar.com", "incorrect-password")
    
    assert exc.value.email == "foo@bar.com"
    assert "incorrect email/password" in str(exc.value)

def test_authenticate_not_found_user():
    auth  = AuthRepository()

    with pytest.raises(UserNotFoundException) as exc:
        auth.authenticate("foo@bar.com", "test")
    
    assert exc.value.email == "foo@bar.com"
    assert "the given user credential is not found" in str(exc.value)
