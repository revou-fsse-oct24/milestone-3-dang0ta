from werkzeug.test import Client
from auth_jwt.tokens import create_access_token
from models import Transaction
from db.users import create_user
from models import Account
from db.accounts import create_account
from db.transactions import withdraw, deposit, transfer
def test_get_transactions_unauthenticated(client):
    response = client.get("/transactions/")
    assert response.status_code == 401

def test_get_transactions_authenticated(app, client, test_user):
    id = create_user(test_user)
    account = Account(balance=1337)
    account_id = create_account(user_id=id, account=account)
    deposit(account_id=account_id, amount=1000)
    
    # Create token within app context
    with app.app_context():
        token = create_access_token(identity=id)
        response = client.get("/transactions/", headers={"Authorization": f"Bearer {token}"})
        
    
    # Verify successful response
    assert response.status_code == 200, response.get_json()
    
    # Verify response data
    data = response.get_json()
    
    assert "transactions" in data
    assert len(data["transactions"]) == 1
    assert data["transactions"][0]["account_id"] == "1"
    assert data["transactions"][0]["amount"] == 1000
    assert data["transactions"][0]["transaction_type"] == "deposit", data["transactions"][0]["transaction_type"]

def test_get_transactions_with_query(app, client, test_user):
    id = create_user(test_user)
    account = Account(balance=1337)
    account_id = create_account(user_id=id, account=account)
    deposit(account_id=account_id, amount=1000)
    
    with app.app_context():
        token = create_access_token(identity=id)
    
    # Test querying transactions with filter
    response = client.get(
        "/transactions/",
        headers={"Authorization": f"Bearer {token}"},
        json={"account_id": account_id, "transaction_type": "deposit"}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert "transactions" in data
    assert len(data["transactions"]) == 1

def test_get_transaction_by_id(app, client, test_user):
    id = create_user(test_user)
    account = Account(balance=1337)
    account_id = create_account(user_id=id, account=account)
    transaction = deposit(account_id=account_id, amount=1000)
    with app.app_context():
        token = create_access_token(identity=id)
        response = client.get(f"/transactions/{transaction.id}", headers={"Authorization": f"Bearer {token}"})
    
    
    assert response.status_code == 200
    data = response.get_json()
    assert "transaction" in data
    assert data["transaction"]["account_id"] == "1"
    assert data["transaction"]["amount"] == 1000

def test_get_nonexistent_transaction(client):
    response = client.get("/transactions/nonexistent")
    assert response.status_code == 404

def test_withdraw(app, client, test_user):
    id = create_user(test_user)
    account = Account(balance=1337)
    account_id = create_account(user_id=id, account=account)
    
    with app.app_context():
        token = create_access_token(identity=id)
        response = client.post(
            "/transactions/withdraw", 
            headers={"Authorization": f"Bearer {token}"},
            json={
                "account_id": str(account_id),
                "amount": 200
            }
        )

    assert response.status_code == 200, response.get_json()
    data = response.get_json()
    assert data["transaction"]["account_id"] == "1"
    assert data["transaction"]["amount"] == 200
    assert data["transaction"]["transaction_type"] == "withdraw"
    
    