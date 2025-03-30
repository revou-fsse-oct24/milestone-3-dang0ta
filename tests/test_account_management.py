from werkzeug import Client
from typing import List
from models import Account

class TestGetAccounts:
    """ this tests GET /accounts/ """
    def test_get_current_user_accounts(self, client: Client, access_token: str, test_user_with_accounts: List[Account]):
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
        response = client.get("/accounts/")
        assert response.status_code == 401, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Unauthorized" in error, error

    def test_get_current_user_accounts_no_accounts(self, client: Client, access_token: str):
        response = client.get("/accounts/", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200, response.get_data()
        response_data = response.get_json()
        assert "accounts" in response_data
        assert len(response_data["accounts"]) == 0
        assert response_data["accounts"] == []

    def test_get_current_user_accounts_invalid_token(self, client: Client):
        response = client.get("/accounts/", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Invalid Token" in error, error

class TestGetAccountById:
    """ this tests GET /accounts/<account_id> """
    def test_get_account_by_id(self, client: Client, access_token: str, test_user_with_account_id: str):
        response = client.get(f"/accounts/{test_user_with_account_id}", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200, response.get_data()
        response_data = response.get_json()
        assert "balance" in response_data
        assert response_data["balance"] == 1000

    def test_get_account_by_id_unauthorized(self, client: Client):
        response = client.get("/accounts/1")
        assert response.status_code == 401, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Unauthorized" in error, error

    def test_get_account_by_id_invalid_token(self, client: Client):
        response = client.get("/accounts/1", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Invalid Token" in error, error

    def test_get_account_by_id_nonexistent(self, client: Client, access_token: str):
        response = client.get("/accounts/1", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 404, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Account not found" in error, error

class TestCreateAccount:
    """ this tests POST /accounts/ """
    def test_create_account(self, client: Client, access_token: str):
        response = client.post("/accounts/", headers={"Authorization": f"Bearer {access_token}"}, json={"balance": 1000})
        assert response.status_code == 201, response.get_data()
        response_json = response.get_json()
        assert "account_id" in response_json

    def test_create_account_unauthorized(self, client: Client):
        response = client.post("/accounts/", json={"balance": 1000})
        assert response.status_code == 401, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Unauthorized" in error, error

    def test_create_account_invalid_token(self, client: Client):
        response = client.post("/accounts/", headers={"Authorization": "Bearer invalid_token"}, json={"balance": 1000})
        assert response.status_code == 401, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Invalid Token" in error, error

    def test_create_account_invalid_json(self, client: Client, access_token: str):
        response = client.post("/accounts/", headers={"Authorization": f"Bearer {access_token}"}, json={"balance": "invalid"})
        assert response.status_code == 400, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "invalid balance" in error, error

class TestUpdateAccount:
    """ this tests PUT /accounts/<account_id> """
    def test_update_account(self, client: Client, access_token: str, test_user_with_account_id: str):
        response = client.put(f"/accounts/{test_user_with_account_id}", headers={"Authorization": f"Bearer {access_token}"}, json={"balance": 2000})
        assert response.status_code == 200, response.get_data()
        response_json = response.get_json()
        assert "balance" in response_json
        assert response_json["balance"] == 2000

    def test_update_account_unauthorized(self, client: Client):
        response = client.put("/accounts/1", json={"balance": 2000})
        assert response.status_code == 401, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Unauthorized" in error, error

    def test_update_account_invalid_token(self, client: Client):
        response = client.put("/accounts/1", headers={"Authorization": "Bearer invalid_token"}, json={"balance": 2000})
        assert response.status_code == 401, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Invalid Token" in error, error

    def test_update_account_invalid_json(self, client: Client, access_token: str):
        response = client.put("/accounts/1", headers={"Authorization": f"Bearer {access_token}"}, json={"balance": "invalid"})
        assert response.status_code == 400, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "invalid balance" in error, error

    def test_update_account_nonexistent(self, client: Client, access_token: str):
        response = client.put("/accounts/1", headers={"Authorization": f"Bearer {access_token}"}, json={"balance": 2000})
        assert response.status_code == 404, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Account not found" in error, error

class TestDeleteAccount:
    """ this tests DELETE /accounts/<account_id> """
    def test_delete_account(self, client: Client, access_token: str, test_user_with_account_id: str):
        response = client.delete(f"/accounts/{test_user_with_account_id}", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200, response.get_data()
        response_json = response.get_json()
        assert "result" in response_json
        assert response_json["result"] == "deleted"   

    def test_delete_account_unauthorized(self, client: Client):
        response = client.delete("/accounts/1")
        assert response.status_code == 401, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Unauthorized" in error, error

    def test_delete_account_invalid_token(self, client: Client):
        response = client.delete("/accounts/1", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Invalid Token" in error, error

    def test_delete_account_nonexistent(self, client: Client, access_token: str):
        response = client.delete("/accounts/1", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 404, response.get_data()
        response_json = response.get_json()
        assert "error" in response_json
        error = response_json["error"]
        assert "Account not found" in error, error
