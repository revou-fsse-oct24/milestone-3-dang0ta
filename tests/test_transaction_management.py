from typing import List
from flask.testing import FlaskClient
from models import Transaction
from pytest import fail

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

        
    

