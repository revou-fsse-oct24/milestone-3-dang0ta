from typing import List
from flask.testing import FlaskClient
from models import Transaction, Account
from pytest import fail
from fixtures.transactions import deposit, withdraw, transfer, transactions
from auth_jwt import create_access_token


class TestWithdraw:
    def test_ok(self, client: FlaskClient, access_token: str, account_id: str) -> Transaction:
        response = client.post("/transactions/withdraw", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 101, "account_id": account_id})
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transaction" in response_json, f"invalid withdraw response, no key 'transaction' found"
        Transaction(**response_json["transaction"])
    
    def test_not_found(self, client: FlaskClient, access_token: str) -> Transaction:
        response = client.post("/transactions/withdraw", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 101, "account_id":"foo"})
        assert response.status_code == 404
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "account not found" in response_json["error"]

    def test_invalid_request(self, client: FlaskClient, access_token: str, account_id: str) -> Transaction:
        response = client.post("/transactions/withdraw", headers={"Authorization": f"Bearer {access_token}"}, json={"amount":"foo", "account_id": account_id})
        assert response.status_code == 400
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "invalid fields: amount" in response_json["error"]

    def test_missing_amount(self, client: FlaskClient, access_token: str, account_id: str) -> Transaction:
        response = client.post("/transactions/withdraw", headers={"Authorization": f"Bearer {access_token}"}, json={"account_id": account_id})
        assert response.status_code == 400
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "invalid fields: amount" in response_json["error"]

    # TODO: maybe use the default account in this case? 
    def test_missing_account_id(self, client: FlaskClient, access_token: str, account_id: str) -> Transaction:
        response = client.post("/transactions/withdraw", headers={"Authorization": f"Bearer {access_token}"}, json={"amount":100})
        assert response.status_code == 400
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "invalid fields: account_id" in response_json["error"]

class TestDeposit:
    def test_ok(self, client: FlaskClient, access_token: str, account_id: str) -> Transaction:
        response = client.post("/transactions/deposit", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 101, "account_id": account_id})
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transaction" in response_json, f"invalid withdraw response, no key 'transaction' found"
        Transaction(**response_json["transaction"])
    
    def test_not_found(self, client: FlaskClient, access_token: str) -> Transaction:
        response = client.post("/transactions/deposit", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 101, "account_id":"foo"})
        assert response.status_code == 404
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "account not found" in response_json["error"]

    def test_invalid_request(self, client: FlaskClient, access_token: str, account_id: str) -> Transaction:
        response = client.post("/transactions/deposit", headers={"Authorization": f"Bearer {access_token}"}, json={"amount":"foo", "account_id": account_id})
        assert response.status_code == 400
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "invalid fields: amount" in response_json["error"]

    def test_missing_amount(self, client: FlaskClient, access_token: str, account_id: str) -> Transaction:
        response = client.post("/transactions/deposit", headers={"Authorization": f"Bearer {access_token}"}, json={"account_id": account_id})
        assert response.status_code == 400
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "invalid fields: amount" in response_json["error"]

    # TODO: maybe use the default account in this case? 
    def test_missing_account_id(self, client: FlaskClient, access_token: str, account_id: str) -> Transaction:
        response = client.post("/transactions/deposit", headers={"Authorization": f"Bearer {access_token}"}, json={"amount":100})
        assert response.status_code == 400
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "invalid fields: account_id" in response_json["error"]

class TestTransfer:
    def test_ok(self, client: FlaskClient, access_token: str, account_id: str, account_id_2: str) -> Transaction:
        response = client.post("/transactions/transfer", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 101, "account_id": account_id, "recipient_account_id": account_id_2})
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transaction" in response_json, f"invalid withdraw response, no key 'transaction' found"
        Transaction(**response_json["transaction"])
    
    def test_not_found_sender(self, client: FlaskClient, access_token: str, account_id_2: str) -> Transaction:
        response = client.post("/transactions/transfer", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 101, "account_id":"foo", "recipient_account_id": account_id_2})
        assert response.status_code == 404
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "account not found" in response_json["error"]
    
    def test_not_found_recipient(self, client: FlaskClient, access_token: str, account_id: str) -> Transaction:
        response = client.post("/transactions/transfer", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 101, "account_id":account_id, "recipient_account_id": "foo"})
        assert response.status_code == 404
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "account not found" in response_json["error"]

    def test_invalid_request(self, client: FlaskClient, access_token: str, account_id: str, account_id_2: str) -> Transaction:
        response = client.post("/transactions/transfer", headers={"Authorization": f"Bearer {access_token}"}, json={"amount":"foo", "account_id": account_id, "recipient_account_id": account_id_2})
        assert response.status_code == 400
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "invalid fields: amount" in response_json["error"]

    def test_missing_amount(self, client: FlaskClient, access_token: str, account_id: str, account_id_2: str) -> Transaction:
        response = client.post("/transactions/transfer", headers={"Authorization": f"Bearer {access_token}"}, json={"account_id": account_id, "recipient_account_id": account_id_2})
        assert response.status_code == 400
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "invalid fields: amount" in response_json["error"]

    # TODO: maybe use the default account in this case? 
    def test_missing_account_id(self, client: FlaskClient, access_token: str, account_id: str, account_id_2: str) -> Transaction:
        response = client.post("/transactions/transfer", headers={"Authorization": f"Bearer {access_token}"}, json={"amount":100, "recipient_account_id": account_id_2})
        assert response.status_code == 400
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "invalid fields: account_id" in response_json["error"]
class TestGetTransactions:
    def test_get_transactions(self, client: FlaskClient, deposit: Transaction, withdraw: Transaction, transfer: Transaction,  access_token: str):
        response = client.get("/transactions", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        response_json = response.get_json()
        assert "transactions" in response_json, "no transactions in response JSON"
        transactions = response_json["transactions"]
        assert len(transactions) == 3, f"expected 3 transactions, got {len(transactions)}"
        for transaction in transactions:
            tr = Transaction(**transaction)
            match tr.transaction_type:
                case "withdraw":
                    assert tr.amount == withdraw.amount
                    assert tr.account_id == withdraw.account_id
                case "deposit":
                    assert tr.amount == deposit.amount
                    assert tr.account_id == deposit.account_id
                case "transfer":
                    assert tr.amount == transfer.amount
                    assert tr.account_id == transfer.account_id
                    assert tr.recipient_id == transfer.recipient_id
                case _:
                    fail(f"unknown transction type: {tr.transaction_type}")

    def test_get_empty_transaction_types(self, client: FlaskClient, deposit: Transaction, withdraw: Transaction, transfer: Transaction,  access_token: str):
        response = client.get("/transactions?transaction_type=", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        response_json = response.get_json()
        assert "transactions" in response_json, "no transactions in response JSON"
        transactions = response_json["transactions"]
        assert len(transactions) == 3, f"expected 3 transactions, got {len(transactions)}"
        for transaction in transactions:
            tr = Transaction(**transaction)
            match tr.transaction_type:
                case "withdraw":
                    assert tr.amount == withdraw.amount
                    assert tr.account_id == withdraw.account_id
                case "deposit":
                    assert tr.amount == deposit.amount
                    assert tr.account_id == deposit.account_id
                case "transfer":
                    assert tr.amount == transfer.amount
                    assert tr.account_id == transfer.account_id
                    assert tr.recipient_id == transfer.recipient_id
                case _:
                    fail(f"unknown transction type: {tr.transaction_type}")

    def test_get_deposit(self, client: FlaskClient, access_token: str, deposit: Transaction, withdraw: Transaction, transfer: Transaction):
        response = client.get("/transactions?transaction_type=deposit", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        response_json = response.get_json()
        assert "transactions" in response_json
        transactions = response_json["transactions"]

        assert len(transactions) == 1, f"expected 1 transaction, got {len(transactions)}"
        transaction = Transaction(**transactions[0])
        assert transaction.amount == deposit.amount
        
        
    def test_get_withdraw(self, client: FlaskClient, access_token: str, deposit: Transaction, withdraw: Transaction, transfer: Transaction):
        response = client.get("/transactions?transaction_type=withdraw", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        response_json = response.get_json()
        assert "transactions" in response_json
        transactions = response_json["transactions"]

        assert len(transactions) == 1, f"expected 1 transaction, got {len(transactions)}"
        transaction = Transaction(**transactions[0])
        assert transaction.amount == withdraw.amount

    def test_get_transfer(self, client: FlaskClient, access_token: str, deposit: Transaction, withdraw: Transaction, transfer: Transaction):
        response = client.get("/transactions?transaction_type=transfer", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        response_json = response.get_json()
        assert "transactions" in response_json
        transactions = response_json["transactions"]

        assert len(transactions) == 1, f"expected 1 transaction, got {len(transactions)}"
        transaction = Transaction(**transactions[0])
        assert transaction.amount == transfer.amount

    def test_get_invalid_transaction_types(self, client: FlaskClient, access_token:str, deposit: Transaction, withdraw: Transaction, transfer: Transaction):
        response = client.get("/transactions?transaction_type=foo", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 400

    def test_get_2_transaction_types(self, client: FlaskClient, access_token:str, deposit: Transaction, withdraw: Transaction, transfer: Transaction):
        response = client.get("/transactions?transaction_type=transfer,deposit", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        response_json = response.get_json()
        assert "transactions" in response_json, "no transactions in response JSON"
        transactions = response_json["transactions"]
        assert len(transactions) == 2, f"expected 2 transactions, got {len(transactions)}"
        for transaction in transactions:
            tr = Transaction(**transaction)
            match tr.transaction_type:
                case "withdraw":
                    fail(f"expecting no transaction with type 'withdraw'")
                case "deposit":
                    assert tr.amount == deposit.amount
                    assert tr.account_id == deposit.account_id
                case "transfer":
                    assert tr.amount == transfer.amount
                    assert tr.account_id == transfer.account_id
                    assert tr.recipient_id == transfer.recipient_id
                case _:
                    fail(f"unknown transction type: {tr.transaction_type}")

    def test_get_3_transaction_types(self, client: FlaskClient, access_token:str, deposit: Transaction, withdraw: Transaction, transfer: Transaction):
        response = client.get("/transactions?transaction_type=withdraw,transfer,deposit", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        response_json = response.get_json()
        assert "transactions" in response_json, "no transactions in response JSON"
        transactions = response_json["transactions"]
        assert len(transactions) == 3, f"expected 3 transactions, got {len(transactions)}"
        for transaction in transactions:
            tr = Transaction(**transaction)
            match tr.transaction_type:
                case "withdraw":
                    assert tr.amount == withdraw.amount
                    assert tr.account_id == withdraw.account_id
                case "deposit":
                    assert tr.amount == deposit.amount
                    assert tr.account_id == deposit.account_id
                case "transfer":
                    assert tr.amount == transfer.amount
                    assert tr.account_id == transfer.account_id
                    assert tr.recipient_id == transfer.recipient_id
                case _:
                    fail(f"unknown transction type: {tr.transaction_type}")

    def test_get_3_transaction_types_with_invalid_types(self, client: FlaskClient, access_token:str, deposit: Transaction, withdraw: Transaction, transfer: Transaction):
        response = client.get("/transactions?transaction_type=withdraw,foo,deposit", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 400


    def test_query_by_account_id(self, client: FlaskClient, access_token:str, withdraw: Transaction):
        response = client.get(f"/transactions?account_id={withdraw.account_id}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transactions" in response_json
        transactions = [Transaction(**transaction) for transaction in response_json["transactions"]]
        assert len(transactions) == 1
        transaction = transactions[0]
        assert transaction.account_id == withdraw.account_id
        assert transaction.amount == withdraw.amount

    def test_query_by_nonexisting_account_id(self, client: FlaskClient, access_token: str):
        response = client.get("/transactions?account_id=foo", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transactions" in  response_json
        assert len(response_json["transactions"]) == 0

    def test_query_by_range(self, client: FlaskClient, access_token: str, transactions: List[Transaction]):
        response = client.get(f"/transactions?range_from={transactions[0].timestamp.isoformat()}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transactions" in response_json
        assert len(response_json["transactions"]) == 3

        response = client.get(f"/transactions?range_from={transactions[1].timestamp.isoformat()}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transactions" in response_json
        assert len(response_json["transactions"]) == 2

        response = client.get(f"/transactions?range_from={transactions[2].timestamp.isoformat()}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transactions" in response_json
        assert len(response_json["transactions"]) == 1

        response = client.get(f"/transactions?range_to={transactions[2].timestamp.isoformat()}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transactions" in response_json
        assert len(response_json["transactions"]) == 3

        response = client.get(f"/transactions?range_to={transactions[1].timestamp.isoformat()}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transactions" in response_json
        assert len(response_json["transactions"]) == 2

        response = client.get(f"/transactions?range_to={transactions[0].timestamp.isoformat()}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transactions" in response_json
        assert len(response_json["transactions"]) == 1

        response = client.get(f"/transactions?range_from={transactions[0].timestamp.isoformat()}&&range_to={transactions[2].timestamp.isoformat()}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transactions" in response_json
        assert len(response_json["transactions"]) == 3

        response = client.get(f"/transactions?range_from={transactions[1].timestamp.isoformat()}&&range_to={transactions[2].timestamp.isoformat()}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transactions" in response_json
        assert len(response_json["transactions"]) == 2

        response = client.get(f"/transactions?range_from={transactions[0].timestamp.isoformat()}&&range_to={transactions[1].timestamp.isoformat()}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transactions" in response_json
        assert len(response_json["transactions"]) == 2

        response = client.get(f"/transactions?range_from={transactions[0].timestamp.isoformat()}&&range_to={transactions[0].timestamp.isoformat()}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transactions" in response_json
        assert len(response_json["transactions"]) == 1
                 
class TestGetTransaction:
    def test_get_existing_withdraw(self, client: FlaskClient, access_token: str, withdraw: Transaction):
        response = client.get(f"/transactions/{withdraw.id}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transaction" in response_json
        transaction = Transaction(**response_json["transaction"])
        assert transaction.id == withdraw.id
        assert transaction.account_id == withdraw.account_id
        assert transaction.amount == withdraw.amount
        assert transaction.recipient_id is None
        assert transaction.transaction_type == "withdraw"

    def test_get_existing_deposit(self, client: FlaskClient, access_token: str, deposit: Transaction):
        response = client.get(f"/transactions/{deposit.id}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transaction" in response_json
        transaction = Transaction(**response_json["transaction"])
        assert transaction.id == deposit.id
        assert transaction.account_id == deposit.account_id
        assert transaction.amount == deposit.amount
        assert transaction.recipient_id is None
        assert transaction.transaction_type == "deposit"

    def test_get_existing_transfer(self, client: FlaskClient, access_token: str, transfer: Transaction):
        response = client.get(f"/transactions/{transfer.id}", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transaction" in response_json
        transaction = Transaction(**response_json["transaction"])
        assert transaction.id == transfer.id
        assert transaction.account_id == transfer.account_id
        assert transaction.amount == transfer.amount
        assert transaction.recipient_id is transfer.recipient_id
        assert transaction.transaction_type == "transfer"

    def test_get_nonexisting_transaction(self, client: FlaskClient, access_token: str):
        response = client.get(f"/transactions/foo", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 404
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "transaction not found" in response_json["error"]