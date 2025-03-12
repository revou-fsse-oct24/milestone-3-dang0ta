from werkzeug.test import Client
from auth_jwt.tokens import create_access_token, create_refresh_token, decode_token

def test_login_success(app_with_test_data, test_user):
    client = app_with_test_data.test_client()
    
    response = client.post(
        "/auth/login",
        json={"email": test_user.email, "password": test_user.password}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert "refresh_token" in data
    
    # Verify token contains correct identity
    with app_with_test_data.app_context():
        decoded = decode_token(data["access_token"])
        assert decoded["sub"] == "foo"

def test_login_invalid_password(app_with_test_data):
    client = app_with_test_data.test_client()
    
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "wrong_password"}
    )
    
    assert response.status_code == 403

def test_login_nonexistent_user(app_with_test_data):
    client = app_with_test_data.test_client()
    
    response = client.post(
        "/auth/login",
        json={"email": "nonexistent@example.com", "password": "password"}
    )
    
    assert response.status_code == 403

def test_login_missing_email(app_with_test_data):
    client = app_with_test_data.test_client()
    
    response = client.post(
        "/auth/login",
        json={"password": "password"}
    )
    
    assert response.status_code in [400, 403]  # Either is acceptable

def test_login_missing_password(app_with_test_data):
    client = app_with_test_data.test_client()
    
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com"}
    )
    
    assert response.status_code in [400, 403]  # Either is acceptable

def test_refresh_token_success(app_with_test_data):
    client = app_with_test_data.test_client()
    
    # Create refresh token with app context
    with app_with_test_data.app_context():
        refresh_token = create_refresh_token(identity="foo")
    
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    
    # Verify new token contains correct identity
    with app_with_test_data.app_context():
        decoded = decode_token(data["access_token"])
        assert decoded["sub"] == "foo"

def test_refresh_token_invalid(app_with_test_data):
    client = app_with_test_data.test_client()
    
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": "invalid_token"}
    )
    
    assert response.status_code == 401

def test_refresh_token_access_token(app_with_test_data):
    client = app_with_test_data.test_client()
    
    # Create access token instead of refresh token
    with app_with_test_data.app_context():
        access_token = create_access_token(identity="foo")
    
    # Try to refresh with an access token
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": access_token}
    )
    
    assert response.status_code == 401

def test_logout_success(app_with_test_data):
    client = app_with_test_data.test_client()
    
    # Create token with app context
    with app_with_test_data.app_context():
        access_token = create_access_token(identity="foo")
    
    response = client.get(
        "/auth/logout",
        json={"access_token": access_token}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert "success" in data["message"].lower()
