from werkzeug.test import Client
from auth_jwt.tokens import create_access_token
from models import Account
from db.users import create_user
from db.accounts import create_account

def test_get_accounts_unauthenticated(client):
    response = client.get("/accounts/")
    assert response.status_code == 401

def test_get_accounts_authenticated(app, test_user):
    id = create_user(test_user)
    account = Account(balance=1337)
    create_account(user_id=id, account=account)
    client = app.test_client()
    
    # Create token within app context
    with app.app_context():
        token = create_access_token(identity=id)
        response = client.get("/accounts/", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.get_json()
        assert "accounts" in data
        assert len(data["accounts"]) == 1
        assert data["accounts"][0]["balance"] == 1337

def test_create_account(app, test_user):
    id = create_user(test_user)
    client = app.test_client()
    
    with app.app_context():
        token = create_access_token(identity=id)
    
    # Test creating a new account
    response = client.post(
        "/accounts/", 
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": id, "balance": 500}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert "account_id" in data
    assert data["account_id"] == 1

def test_get_account_by_id(app, test_user):
    id = create_user(test_user)
    account = Account(balance=1337)
    account_id = create_account(user_id=id, account=account)
    client = app.test_client()
    
    with app.app_context():
        token = create_access_token(identity=id)
        response = client.get(
            f"/accounts/{account_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert "balance" in data
        assert data["balance"] == 1337

def test_get_nonexistent_account(app):
    client = app.test_client()
    
    with app.app_context():
        token = create_access_token(identity="foo")
    
    response = client.get(
        "/accounts/nonexistent",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404

def test_update_account(app, test_user):
    id = create_user(test_user)
    account = Account(balance=1337)
    account_id = create_account(user_id=id, account=account)
    client = app.test_client()
    
    with app.app_context():
        token = create_access_token(identity=id)
    
    # Test updating an account
    response = client.put(
        f"/accounts/{account_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": "foo", "balance": 1338}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert "balance" in data
    assert data["balance"] == 1338

def test_delete_account(app, test_user):
    id = create_user(test_user)
    account = Account(balance=1337)
    account_id = create_account(user_id=id, account=account)
    client = app.test_client()
    
    with app.app_context():
        token = create_access_token(identity=id)
    
    # Test deleting an account
    response = client.delete(
        f"/accounts/{account_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == "deleted"
    
    # Verify account is deleted
    response = client.get(
        f"/accounts/{account_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
