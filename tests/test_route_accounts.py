from werkzeug.test import Client
from auth_jwt.tokens import create_access_token
from models import Account

def test_get_accounts_unauthenticated(client):
    response = client.get("/accounts/")
    assert response.status_code == 401

def test_get_accounts_authenticated(app_with_test_data):
    client = app_with_test_data.test_client()
    
    # Create token within app context
    with app_with_test_data.app_context():
        token = create_access_token(identity="foo")
    
    response = client.get("/accounts/", headers={"Authorization": f"Bearer {token}"})
    
    # Verify successful response
    assert response.status_code == 200
    
    # Verify response data
    data = response.get_json()
    assert "accounts" in data
    assert len(data["accounts"]) == 1
    assert data["accounts"][0]["user_id"] == "foo"
    assert data["accounts"][0]["balance"] == 1000

def test_create_account(app_with_test_data):
    client = app_with_test_data.test_client()
    
    with app_with_test_data.app_context():
        token = create_access_token(identity="foo")
    
    # Test creating a new account
    response = client.post(
        "/accounts/", 
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": "foo", "balance": 500}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert "account" in data
    assert data["account"]["user_id"] == "foo"
    assert data["account"]["balance"] == 500

def test_get_account_by_id(app_with_test_data):
    client = app_with_test_data.test_client()
    
    with app_with_test_data.app_context():
        token = create_access_token(identity="foo")
    
    # Test getting a specific account
    response = client.get(
        "/accounts/acc123",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert "account" in data
    assert data["account"]["user_id"] == "foo"
    assert data["account"]["balance"] == 1000

def test_get_nonexistent_account(app_with_test_data):
    client = app_with_test_data.test_client()
    
    with app_with_test_data.app_context():
        token = create_access_token(identity="foo")
    
    response = client.get(
        "/accounts/nonexistent",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404

def test_update_account(app_with_test_data):
    client = app_with_test_data.test_client()
    
    with app_with_test_data.app_context():
        token = create_access_token(identity="foo")
    
    # Test updating an account
    response = client.put(
        "/accounts/acc123",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": "foo", "balance": 2000}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert "account" in data
    assert data["account"]["balance"] == 2000

def test_delete_account(app_with_test_data):
    client = app_with_test_data.test_client()
    
    with app_with_test_data.app_context():
        token = create_access_token(identity="foo")
    
    # Test deleting an account
    response = client.delete(
        "/accounts/acc123",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == "deleted"
    
    # Verify account is deleted
    response = client.get(
        "/accounts/acc123",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
