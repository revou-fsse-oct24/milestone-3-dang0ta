from werkzeug import Client
from typing import List
from models import Account

class TestGetAccounts:
    """Test suite for GET /accounts/ endpoint.
    
    This test suite verifies the functionality of retrieving all accounts for the current user.
    It includes tests for successful retrieval, unauthorized access, empty account list,
    and invalid token scenarios.
    """
    
    def test_get_current_user_accounts(self, client: Client, access_token: str, test_user_with_accounts: List[Account]):
        """Test successful retrieval of current user's accounts.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            test_user_with_accounts: List of test accounts associated with the user
            
        Verifies:
            - Response status code is 200
            - Response contains 'accounts' key
            - Number of accounts matches test data
            - Account balances match test data
        """
        response = client.get("/accounts/", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200, response.get_data()
        response_data = response.get_json()
        assert "accounts" in response_data
        assert len(response_data["accounts"]) == len(test_user_with_accounts)
        print(f"response_data: {response_data}")
        if len(response_data) == 1:
            assert response_data["accounts"][0]["balance"] == test_user_with_accounts[0].balance
        else:
            for i in range(len(response_data)):
                assert response_data["accounts"][i]["balance"] == test_user_with_accounts[i].balance
    
    def test_get_current_user_accounts_unauthorized(self, client: Client):
        """Test unauthorized access to get accounts.
        
        Args:
            client: Flask test client
            
        Verifies:
            - Response status code is 401
            - Response contains error message
            - Error message indicates unauthorized access
        """
        response = client.get("/accounts/")
        assert response.status_code == 401, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Unauthorized" in error, error

    def test_get_current_user_accounts_no_accounts(self, client: Client, access_token: str):
        """Test retrieval when user has no accounts.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            
        Verifies:
            - Response status code is 200
            - Response contains empty accounts list
        """
        response = client.get("/accounts/", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200, response.get_data()
        response_data = response.get_json()
        assert "accounts" in response_data
        assert len(response_data["accounts"]) == 0
        assert response_data["accounts"] == []

    def test_get_current_user_accounts_invalid_token(self, client: Client):
        """Test access with invalid JWT token.
        
        Args:
            client: Flask test client
            
        Verifies:
            - Response status code is 401
            - Response contains error message
            - Error message indicates invalid token
        """
        response = client.get("/accounts/", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Invalid Token" in error, error

class TestGetAccountById:
    """Test suite for GET /accounts/<account_id> endpoint.
    
    This test suite verifies the functionality of retrieving a specific account by ID.
    It includes tests for successful retrieval, unauthorized access, invalid token,
    and non-existent account scenarios.
    """
    
    def test_get_account_by_id(self, client: Client, access_token: str, test_user_with_account_id: str):
        """Test successful retrieval of account by ID.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            test_user_with_account_id: ID of test account
            
        Verifies:
            - Response status code is 200
            - Response contains correct account balance
        """
        response = client.get(f"/accounts/{test_user_with_account_id}", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200, response.get_data()
        response_data = response.get_json()
        assert "balance" in response_data
        assert response_data["balance"] == 1000

    def test_get_account_by_id_unauthorized(self, client: Client):
        """Test unauthorized access to get account by ID.
        
        Args:
            client: Flask test client
            
        Verifies:
            - Response status code is 401
            - Response contains error message
            - Error message indicates unauthorized access
        """
        response = client.get("/accounts/1")
        assert response.status_code == 401, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Unauthorized" in error, error

    def test_get_account_by_id_invalid_token(self, client: Client):
        """Test access with invalid JWT token.
        
        Args:
            client: Flask test client
            
        Verifies:
            - Response status code is 401
            - Response contains error message
            - Error message indicates invalid token
        """
        response = client.get("/accounts/1", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Invalid Token" in error, error

    def test_get_account_by_id_nonexistent(self, client: Client, access_token: str):
        """Test retrieval of non-existent account.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            
        Verifies:
            - Response status code is 404
            - Response contains error message
            - Error message indicates account not found
        """
        response = client.get("/accounts/1", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 404, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Account not found" in error, error

class TestCreateAccount:
    """Test suite for POST /accounts/ endpoint.
    
    This test suite verifies the functionality of creating new accounts.
    It includes tests for successful creation, unauthorized access, invalid token,
    and invalid input data scenarios.
    """
    
    def test_create_account(self, client: Client, access_token: str):
        """Test successful account creation.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            
        Verifies:
            - Response status code is 201
            - Response contains account_id
        """
        response = client.post("/accounts/", headers={"Authorization": f"Bearer {access_token}"}, json={"balance": 1000})
        assert response.status_code == 201, response.get_data()
        response_json = response.get_json()
        assert "account_id" in response_json

    def test_create_account_unauthorized(self, client: Client):
        """Test unauthorized account creation.
        
        Args:
            client: Flask test client
            
        Verifies:
            - Response status code is 401
            - Response contains error message
            - Error message indicates unauthorized access
        """
        response = client.post("/accounts/", json={"balance": 1000})
        assert response.status_code == 401, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Unauthorized" in error, error

    def test_create_account_invalid_token(self, client: Client):
        """Test account creation with invalid JWT token.
        
        Args:
            client: Flask test client
            
        Verifies:
            - Response status code is 401
            - Response contains error message
            - Error message indicates invalid token
        """
        response = client.post("/accounts/", headers={"Authorization": "Bearer invalid_token"}, json={"balance": 1000})
        assert response.status_code == 401, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Invalid Token" in error, error

    def test_create_account_invalid_json(self, client: Client, access_token: str):
        """Test account creation with invalid input data.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            
        Verifies:
            - Response status code is 400
            - Response contains error message
            - Error message indicates invalid balance
        """
        response = client.post("/accounts/", headers={"Authorization": f"Bearer {access_token}"}, json={"balance": "invalid"})
        assert response.status_code == 400, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "invalid balance" in error, error

class TestUpdateAccount:
    """Test suite for PUT /accounts/<account_id> endpoint.
    
    This test suite verifies the functionality of updating existing accounts.
    It includes tests for successful updates, unauthorized access, invalid token,
    invalid input data, and non-existent account scenarios.
    """
    
    def test_update_account(self, client: Client, access_token: str, test_user_with_account_id: str):
        """Test successful account update.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            test_user_with_account_id: ID of test account
            
        Verifies:
            - Response status code is 200
            - Response contains updated balance
        """
        response = client.put(f"/accounts/{test_user_with_account_id}", headers={"Authorization": f"Bearer {access_token}"}, json={"balance": 2000})
        assert response.status_code == 200, response.get_data()
        response_json = response.get_json()
        assert "balance" in response_json
        assert response_json["balance"] == 2000

    def test_update_account_unauthorized(self, client: Client):
        """Test unauthorized account update.
        
        Args:
            client: Flask test client
            
        Verifies:
            - Response status code is 401
            - Response contains error message
            - Error message indicates unauthorized access
        """
        response = client.put("/accounts/1", json={"balance": 2000})
        assert response.status_code == 401, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Unauthorized" in error, error

    def test_update_account_invalid_token(self, client: Client):
        """Test account update with invalid JWT token.
        
        Args:
            client: Flask test client
            
        Verifies:
            - Response status code is 401
            - Response contains error message
            - Error message indicates invalid token
        """
        response = client.put("/accounts/1", headers={"Authorization": "Bearer invalid_token"}, json={"balance": 2000})
        assert response.status_code == 401, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Invalid Token" in error, error

    def test_update_account_invalid_json(self, client: Client, access_token: str):
        """Test account update with invalid input data.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            
        Verifies:
            - Response status code is 400
            - Response contains error message
            - Error message indicates invalid balance
        """
        response = client.put("/accounts/1", headers={"Authorization": f"Bearer {access_token}"}, json={"balance": "invalid"})
        assert response.status_code == 400, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "invalid balance" in error, error

    def test_update_account_nonexistent(self, client: Client, access_token: str):
        """Test update of non-existent account.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            
        Verifies:
            - Response status code is 404
            - Response contains error message
            - Error message indicates account not found
        """
        response = client.put("/accounts/1", headers={"Authorization": f"Bearer {access_token}"}, json={"balance": 2000})
        assert response.status_code == 404, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Account not found" in error, error

class TestDeleteAccount:
    """Test suite for DELETE /accounts/<account_id> endpoint.
    
    This test suite verifies the functionality of deleting accounts.
    It includes tests for successful deletion, unauthorized access, invalid token,
    and non-existent account scenarios.
    """
    
    def test_delete_account(self, client: Client, access_token: str, test_user_with_account_id: str):
        """Test successful account deletion.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            test_user_with_account_id: ID of test account
            
        Verifies:
            - Response status code is 200
            - Response contains deletion confirmation
        """
        response = client.delete(f"/accounts/{test_user_with_account_id}", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200, response.get_data()
        response_json = response.get_json()
        assert "result" in response_json
        assert response_json["result"] == "deleted"   

    def test_delete_account_unauthorized(self, client: Client):
        """Test unauthorized account deletion.
        
        Args:
            client: Flask test client
            
        Verifies:
            - Response status code is 401
            - Response contains error message
            - Error message indicates unauthorized access
        """
        response = client.delete("/accounts/1")
        assert response.status_code == 401, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Unauthorized" in error, error

    def test_delete_account_invalid_token(self, client: Client):
        """Test account deletion with invalid JWT token.
        
        Args:
            client: Flask test client
            
        Verifies:
            - Response status code is 401
            - Response contains error message
            - Error message indicates invalid token
        """
        response = client.delete("/accounts/1", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Invalid Token" in error, error

    def test_delete_account_nonexistent(self, client: Client, access_token: str):
        """Test deletion of non-existent account.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            
        Verifies:
            - Response status code is 404
            - Response contains error message
            - Error message indicates account not found
        """
        response = client.delete("/accounts/1", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 404, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Account not found" in error, error
