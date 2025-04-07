from flask.testing import FlaskClient
from datetime import datetime, timedelta
from models import Bill, CreateBillRequest
from auth_jwt import create_access_token
import zoneinfo
import pytest
from typing import List

@pytest.fixture
def bill(client: FlaskClient, access_token: str) -> Bill:
    now = datetime.now().replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
    response = client.post("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"biller_name": "test", "due_date": now.isoformat(), "amount": 100},follow_redirects=True)
    assert response.status_code == 201, response.get_data()
    assert "application/json" in response.headers.get("Content-Type")
    response_json = response.get_json()
    assert "bill" in response_json
    bill = Bill(**response_json["bill"])
    assert bill.biller_name == "test"
    assert bill.due_date == now
    assert bill.amount == 100

    return bill

@pytest.fixture
def bills(client: FlaskClient, access_token: str, account_id: str, account_id_2: str) -> List[Bill]:
    now = datetime.now().replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
    last_7_days, last_3_days, yesterday = now - timedelta(days=7), now - timedelta(days=3), now - timedelta(days=1)

    requests = [
        CreateBillRequest(biller_name="test-1", due_date=last_7_days, amount=101),
        CreateBillRequest(biller_name="test-2", due_date=last_3_days, amount=102),
        CreateBillRequest(biller_name="test-3", due_date=yesterday, amount=103),
        CreateBillRequest(biller_name="test-4", due_date=now, amount=104),
        CreateBillRequest(biller_name="test-5", due_date=last_7_days, amount=105, account_id=account_id),
        CreateBillRequest(biller_name="test-6", due_date=yesterday, amount=106, account_id=account_id),
        CreateBillRequest(biller_name="test-7", due_date=now, amount=107, account_id=account_id),
        CreateBillRequest(biller_name="test-8", due_date=yesterday, amount=108, account_id=account_id_2),
        CreateBillRequest(biller_name="test-9", due_date=now, amount=109, account_id=account_id_2),
    ]

    bills = []

    for req in requests:
        response = client.post("/bills", headers={"Authorization": f"Bearer {access_token}"}, json=req.model_dump(), follow_redirects=True)
        assert response.status_code == 201, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bill" in response_json
        bill = Bill(**response_json["bill"])
        assert bill.biller_name == req.biller_name
        assert bill.due_date == req.due_date
        assert bill.amount == req.amount   
        bills.append(bill)

    bills.sort(key=bill_key)
    return bills

def bill_key(bill: Bill) -> datetime:
    return bill.due_date

class TestCreateBill:
    def test_default_account(self, client: FlaskClient, access_token: str):
        now = datetime.now().replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
        response = client.post("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"biller_name": "test", "due_date": now.isoformat(), "amount": 100},follow_redirects=True)
        assert response.status_code == 201, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bill" in response_json
        bill = Bill(**response_json["bill"])
        assert bill.biller_name == "test"
        assert bill.due_date == now
        assert bill.amount == 100

    def test_specific_account(self, client: FlaskClient, access_token: str, account_id: str):
        now = datetime.now().replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
        response = client.post("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"biller_name": "test", "due_date": now.isoformat(), "amount": 100, "account_id": account_id},follow_redirects=True)
        assert response.status_code == 201, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bill" in response_json
        bill = Bill(**response_json["bill"])
        assert bill.biller_name == "test"
        assert bill.due_date == now
        assert bill.amount == 100
        assert bill.account_id == account_id

    def test_invalid_account(self, client: FlaskClient, access_token: str, account_id: str):
        now = datetime.now().replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
        response = client.post("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"biller_name": "test", "due_date": now.isoformat(), "amount": 100, "account_id": "invalid_account_id"},follow_redirects=True)
        assert response.status_code == 404, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "error" in response_json
        assert response_json["error"] == "account not found"

    def test_unknown_user(self, client: FlaskClient):
        now = datetime.now().replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
        response = client.post("/bills", headers={"Authorization": f"Bearer {create_access_token(identity="unknown_user")}"}, json={"biller_name": "test", "due_date": now.isoformat(), "amount": 100},follow_redirects=True)
        assert response.status_code == 404, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "error" in response_json
        assert response_json["error"] == "user not found"

    def test_invalid_request(self, client: FlaskClient, access_token: str):
        now = datetime.now().replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
        response = client.post("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"biller_name": "test", "due_date": now.isoformat(), "amount": "invalid_amount"},follow_redirects=True)
        assert response.status_code == 400, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "error" in response_json
        assert response_json["error"] == "invalid fields: amount"


class TestGetBills:
    def test_get_all(self, client: FlaskClient, access_token: str, bills: List[Bill]):
        response = client.get("/bills", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bills" in response_json
        found = [Bill(**bill) for bill in response_json["bills"]]
        assert len(found) == 9
        for bill in found:
            assert bill in bills

    def test_get_existing(self, client: FlaskClient, access_token: str, bill: Bill):    
        response = client.get("/bills", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bills" in response_json
        bills = [Bill(**bill) for bill in response_json["bills"]]
        assert len(bills) == 1
        assert bills[0].id == bill.id
        assert bills[0].biller_name == bill.biller_name
        assert bills[0].due_date == bill.due_date
        assert bills[0].amount == bill.amount

    def test_get_on_default_account(self, client: FlaskClient, access_token: str, bills: List[Bill]):
        response = client.get("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"account_id": "1"}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bills" in response_json
        bills = [Bill(**bill) for bill in response_json["bills"]]
        assert len(bills) == 4
        for bill in bills:
            assert bill.account_id == "1"

    def test_get_on_account_1(self, client: FlaskClient, access_token: str, bills: List[Bill], account_id: str):
        response = client.get("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"account_id": account_id}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bills" in response_json
        bills = [Bill(**bill) for bill in response_json["bills"]]
        assert len(bills) == 3
        for bill in bills:
            assert bill.account_id == account_id

    def test_get_on_account_2(self, client: FlaskClient, access_token: str, bills: List[Bill], account_id_2: str):
        response = client.get("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"account_id": account_id_2}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bills" in response_json
        bills = [Bill(**bill) for bill in response_json["bills"]]
        assert len(bills) == 2
        for bill in bills:
            assert bill.account_id == account_id_2


    def test_get_on_due_date(self, client: FlaskClient, access_token: str, bills: List[Bill]):
        response = client.get("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"due_date_from": bills[0].due_date.isoformat()}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bills" in response_json
        found = [Bill(**bill) for bill in response_json["bills"]]
        assert len(found) == 9
        for bill in found:
            assert bill.due_date >= bills[0].due_date

        response = client.get("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"due_date_from": bills[3].due_date.isoformat()}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bills" in response_json
        found = [Bill(**bill) for bill in response_json["bills"]]
        assert len(found) == 6
        for bill in found:
            assert bill.due_date >= bills[3].due_date

        response = client.get("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"due_date_from": bills[6].due_date.isoformat()}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bills" in response_json
        found = [Bill(**bill) for bill in response_json["bills"]]
        assert len(found) == 3
        for bill in found:
            assert bill.due_date >= bills[6].due_date

        response = client.get("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"due_date_to": bills[6].due_date.isoformat()}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bills" in response_json
        found = [Bill(**bill) for bill in response_json["bills"]]
        assert len(found) == 9
        for bill in found:
            assert bill.due_date <= bills[6].due_date

        response = client.get("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"due_date_to": bills[3].due_date.isoformat()}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bills" in response_json
        found = [Bill(**bill) for bill in response_json["bills"]]
        assert len(found) == 6
        for bill in found:
            assert bill.due_date <= bills[3].due_date
        
        response = client.get("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"due_date_to": bills[0].due_date.isoformat()}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bills" in response_json
        found = [Bill(**bill) for bill in response_json["bills"]]
        assert len(found) == 2
        for bill in found:
            assert bill.due_date <= bills[0].due_date
        

        response = client.get("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"due_date_from": bills[3].due_date.isoformat(), "due_date_to": bills[6].due_date.isoformat()}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bills" in response_json
        found = [Bill(**bill) for bill in response_json["bills"]]
        assert len(found) == 6
        for bill in found:
            assert bill.due_date >= bills[3].due_date
            assert bill.due_date <= bills[6].due_date

    def test_get_on_biller_name(self, client: FlaskClient, access_token: str, bills: List[Bill]):
        biller_names = [bill.biller_name for bill in bills]
        for biller_name in biller_names:
            response = client.get("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"biller_name": biller_name}, follow_redirects=True)
            assert response.status_code == 200, response.get_data()
            assert "application/json" in response.headers.get("Content-Type")
            response_json = response.get_json()
            assert "bills" in response_json
            found = [Bill(**bill) for bill in response_json["bills"]]
            assert len(found) == 1
            assert found[0].biller_name == biller_name
        

    def test_get_on_amount(self, client: FlaskClient, access_token: str, bills: List[Bill]):
        response = client.get("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"amount_min": 101}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bills" in response_json
        found = [Bill(**bill) for bill in response_json["bills"]]
        assert len(found) == 9
        for bill in found:
            assert bill.amount >= 101


        response = client.get("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"amount_min": 106}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bills" in response_json
        found = [Bill(**bill) for bill in response_json["bills"]]
        assert len(found) == 4
        for bill in found:
            assert bill.amount >= 106

        response = client.get("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"amount_min": 108}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bills" in response_json
        found = [Bill(**bill) for bill in response_json["bills"]]
        assert len(found) == 2
        for bill in found:
            assert bill.amount >= 108

        response = client.get("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"amount_max": 109}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bills" in response_json
        found = [Bill(**bill) for bill in response_json["bills"]]
        assert len(found) == 9
        for bill in found:
            assert bill.amount <= 109
        
        response = client.get("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"amount_max": 106}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bills" in response_json
        found = [Bill(**bill) for bill in response_json["bills"]]
        assert len(found) == 6
        for bill in found:
            assert bill.amount <= 106

        response = client.get("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"amount_max": 106, "amount_min": 103}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bills" in response_json
        found = [Bill(**bill) for bill in response_json["bills"]]
        assert len(found) == 4
        for bill in found:
            assert bill.amount <= 106
            assert bill.amount >= 103


    def test_get_on_invalid_request(self, client: FlaskClient, access_token: str):
        response = client.get("/bills", headers={"Authorization": f"Bearer {access_token}"}, json={"amount_min": "foo", "amount_max": "bar"}, follow_redirects=True)
        assert response.status_code == 400, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "error" in response_json
        assert response_json["error"] == "invalid fields: amount_min, amount_max"

    def test_get_on_unknown_user(self, client: FlaskClient):
        response = client.get("/bills", headers={"Authorization": f"Bearer {create_access_token(identity="unknown_user")}"}, follow_redirects=True)
        assert response.status_code == 404, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "error" in response_json
        assert response_json["error"] == "user not found"

class TestGetBill:
    def test_get_all(self, client: FlaskClient, access_token: str, bills: List[Bill]):
        for bill in bills:
            response = client.get(f"/bills/{bill.id}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
            assert response.status_code == 200, response.get_data()
            assert "application/json" in response.headers.get("Content-Type")
            response_json = response.get_json()
            assert "bill" in response_json
            found = Bill(**response_json["bill"])
            assert found.id == bill.id
            assert found.biller_name == bill.biller_name
            assert found.due_date == bill.due_date
            assert found.amount == bill.amount

    def test_get_on_unknown_bill(self, client: FlaskClient, access_token: str):
        response = client.get("/bills/unknown_bill", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 404, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "error" in response_json
        assert response_json["error"] == "the bill can't be found"

    def test_get_on_unknown_user(self, client: FlaskClient):
        response = client.get("/bills/unknown_bill", headers={"Authorization": f"Bearer {create_access_token(identity="unknown_user")}"}, follow_redirects=True)
        assert response.status_code == 404, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "error" in response_json
        assert response_json["error"] == "user not found"

class TestUpdateBill:
    def test_update_all(self, client: FlaskClient, access_token: str, bill: Bill):
        response = client.put(f"/bills/{bill.id}", headers={"Authorization": f"Bearer {access_token}"}, json={"biller_name": "test-updated", "due_date":(bill.due_date + timedelta(days=1)).isoformat(), "amount": 100}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bill" in response_json
        found = Bill(**response_json["bill"])
        assert found.id == bill.id
        assert found.biller_name == "test-updated"
        assert found.due_date == bill.due_date + timedelta(days=1)
        assert found.amount == 100

        response = client.get(f"/bills/{bill.id}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "bill" in response_json
        found = Bill(**response_json["bill"])
        assert found.id == bill.id
        assert found.biller_name == "test-updated"
        assert found.due_date == bill.due_date + timedelta(days=1)
        assert found.amount == 100


    def test_update_on_unknown_bill(self, client: FlaskClient, access_token: str):
        response = client.put("/bills/unknown_bill", headers={"Authorization": f"Bearer {access_token}"}, json={"biller_name": "test-updated", "amount": 100}, follow_redirects=True)
        assert response.status_code == 404, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "error" in response_json
        assert response_json["error"] == "the bill can't be found"

    def test_update_on_unknown_user(self, client: FlaskClient):
        response = client.put("/bills/unknown_bill", headers={"Authorization": f"Bearer {create_access_token(identity="unknown_user")}"}, json={"biller_name": "test-updated", "amount": 100}, follow_redirects=True)
        assert response.status_code == 404, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "error" in response_json
        assert response_json["error"] == "user not found"

    def test_update_on_invalid_request(self, client: FlaskClient, access_token: str):
        response = client.put("/bills/unknown_bill", headers={"Authorization": f"Bearer {access_token}"}, json={"biller_name": "test-updated", "amount": "invalid_amount"}, follow_redirects=True)
        assert response.status_code == 400, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "error" in response_json
        assert response_json["error"] == "invalid fields: amount"


class TestDeleteBill:
    def test_delete_all(self, client: FlaskClient, access_token: str, bills: List[Bill]):
        for bill in bills:
            response = client.delete(f"/bills/{bill.id}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
            assert response.status_code == 200, response.get_data()
            assert "application/json" in response.headers.get("Content-Type")
            response_json = response.get_json()
            assert "status" in response_json
            assert response_json["status"] == "deleted"

            response = client.get(f"/bills/{bill.id}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
            assert response.status_code == 404, response.get_data()
            assert "application/json" in response.headers.get("Content-Type")
            response_json = response.get_json()
            assert "error" in response_json
            assert response_json["error"] == "the bill can't be found"

    def test_delete_on_unknown_bill(self, client: FlaskClient, access_token: str):
        response = client.delete("/bills/unknown_bill", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 404, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "error" in response_json
        assert response_json["error"] == "the bill can't be found"

    def test_delete_on_unknown_user(self, client: FlaskClient):
        response = client.delete("/bills/unknown_bill", headers={"Authorization": f"Bearer {create_access_token(identity="unknown_user")}"}, follow_redirects=True)
        assert response.status_code == 404, response.get_data()
        assert "application/json" in response.headers.get("Content-Type")
        response_json = response.get_json()
        assert "error" in response_json
        assert response_json["error"] == "user not found"
