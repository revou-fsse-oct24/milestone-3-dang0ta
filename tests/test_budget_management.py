from flask.testing import FlaskClient
import pytest
from models import  CreateBudgetRequest, Budget
from datetime import datetime, timezone, timedelta


@pytest.fixture
def create_budget_request() -> CreateBudgetRequest:
    return CreateBudgetRequest(name="test budget", amount=1000, start_date=datetime.now(tz=timezone.utc), end_date=datetime.now(tz=timezone.utc) + timedelta(days=1))

@pytest.fixture
def test_budget(client: FlaskClient, access_token:str, create_budget_request: CreateBudgetRequest) -> Budget:
    response = client.post("/budgets", headers={"Authorization": f"Bearer {access_token}"}, json=create_budget_request.model_dump(), follow_redirects=True)
    assert response.status_code == 200, response.get_data()
    assert "application/json" in response.headers.get("content-type")
    response_json = response.get_json()
    assert "budget" in response_json
    budget = Budget(**response_json["budget"])
    assert budget.amount == create_budget_request.amount
    assert budget.name == create_budget_request.name
    assert budget.start_date == create_budget_request.start_date
    assert budget.end_date == create_budget_request.end_date
    return budget


class TestCreateBudget:
    def test_create_ok(self, client: FlaskClient, access_token:str, create_budget_request: CreateBudgetRequest):
        response = client.post("/budgets", headers={"Authorization": f"Bearer {access_token}"}, json=create_budget_request.model_dump(), follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "budget" in response_json
        budget = Budget(**response_json["budget"])
        assert budget.amount == create_budget_request.amount
        assert budget.name == create_budget_request.name
        assert budget.start_date == create_budget_request.start_date
        assert budget.end_date == create_budget_request.end_date

class TestGetBudgets:
    def test_get_ok(self, client: FlaskClient, access_token: str, test_budget: Budget):
        response = client.get(f"/budgets", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "budgets" in response_json
        budgets = [Budget(**budget) for budget in response_json["budgets"]]
        assert len(budgets) == 1
        budget = budgets[0]
        assert test_budget.id == budget.id
        assert test_budget.name == budget.name
        assert test_budget.amount == budget.amount
        assert test_budget.start_date == budget.start_date
        assert test_budget.end_date == budget.end_date
        assert test_budget.user.name == budget.user.name

class TestGetBudget:
    def test_get_ok(self, client: FlaskClient, access_token: str, test_budget: Budget):
        response = client.get(f"/budgets/{test_budget.id}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "budget" in response_json
        budget = Budget(**response_json["budget"])        
        assert test_budget.id == budget.id
        assert test_budget.name == budget.name
        assert test_budget.amount == budget.amount
        assert test_budget.start_date == budget.start_date
        assert test_budget.end_date == budget.end_date
        assert test_budget.user.name == budget.user.name

class TestUpdateBudget:
    def test_update_ok(self, client: FlaskClient, access_token: str, test_budget: Budget):
        response = client.put(f"/budgets/{test_budget.id}", headers={"Authorization": f"Bearer {access_token}"}, json={"name": "test updated"}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "budget" in response_json
        budget = Budget(**response_json["budget"])        
        assert test_budget.id == budget.id
        assert "test updated" == budget.name
        assert test_budget.amount == budget.amount
        assert test_budget.start_date == budget.start_date
        assert test_budget.end_date == budget.end_date
        assert test_budget.user.name == budget.user.name

class TestDeleteBudget:
    def test_delete_ok(self, client: FlaskClient, access_token: str, test_budget: Budget):
        id=test_budget.id
        response = client.delete(f"/budgets/{id}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "result" in response_json
        assert "deleted" in response_json["result"]

        response = client.get(f"/budgets/{id}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 404, response.get_data()
