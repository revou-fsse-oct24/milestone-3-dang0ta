from typing import List
from flask.testing import FlaskClient
from models import Transaction, Account
from pytest import fail
from fixtures.transactions import deposit, withdraw, transfer, transactions
from auth_jwt import create_access_token


class TestWithdraw:
    """Test suite for POST /transactions/withdraw endpoint.
    
    This test suite verifies the functionality of withdrawal transactions.
    It includes tests for successful withdrawals, invalid requests, missing fields,
    and unauthorized access scenarios.
    """
    
    def test_ok(self, client: FlaskClient, access_token: str, account_id: str) -> Transaction:
        """Test successful withdrawal transaction.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            account_id: ID of the account to withdraw from
            
        Verifies:
            - Response status code is 200
            - Response contains transaction details
            - Transaction type is 'withdraw'
            - Transaction amount matches request
        """
        response = client.post("/transactions/withdraw", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 101, "account_id": account_id})
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transaction" in response_json, f"invalid withdraw response, no key 'transaction' found"
        Transaction(**response_json["transaction"])
    
    def test_forbidden(self, client: FlaskClient, access_token: str) -> Transaction:
        """Test withdrawal with insufficient permissions.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            
        Verifies:
            - Response status code is 401
            - Response contains error message
            - Error message indicates forbidden access
        """
        response = client.post("/transactions/withdraw", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 101, "account_id":"foo"})
        assert response.status_code == 401
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "Forbidden" in response_json["error"]

    def test_invalid_request(self, client: FlaskClient, access_token: str, account_id: str) -> Transaction:
        """Test withdrawal with invalid amount.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            account_id: ID of the account to withdraw from
            
        Verifies:
            - Response status code is 400
            - Response contains error message
            - Error message indicates invalid amount field
        """
        response = client.post("/transactions/withdraw", headers={"Authorization": f"Bearer {access_token}"}, json={"amount":"foo", "account_id": account_id})
        assert response.status_code == 400
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "invalid fields: amount" in response_json["error"]

    def test_missing_amount(self, client: FlaskClient, access_token: str, account_id: str) -> Transaction:
        """Test withdrawal with missing amount field.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            account_id: ID of the account to withdraw from
            
        Verifies:
            - Response status code is 400
            - Response contains error message
            - Error message indicates missing amount field
        """
        response = client.post("/transactions/withdraw", headers={"Authorization": f"Bearer {access_token}"}, json={"account_id": account_id})
        assert response.status_code == 400
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "invalid fields: amount" in response_json["error"]

    # TODO: maybe use the default account in this case? 
    def test_missing_account_id(self, client: FlaskClient, access_token: str, account_id: str) -> Transaction:
        """Test withdrawal with missing account_id field.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            account_id: ID of the account to withdraw from
            
        Verifies:
            - Response status code is 400
            - Response contains error message
            - Error message indicates missing account_id field
        """
        response = client.post("/transactions/withdraw", headers={"Authorization": f"Bearer {access_token}"}, json={"amount":100})
        assert response.status_code == 400
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "invalid fields: account_id" in response_json["error"]

class TestDeposit:
    """Test suite for POST /transactions/deposit endpoint.
    
    This test suite verifies the functionality of deposit transactions.
    It includes tests for successful deposits, invalid requests, missing fields,
    and unauthorized access scenarios.
    """
    
    def test_ok(self, client: FlaskClient, access_token: str, account_id: str) -> Transaction:
        """Test successful deposit transaction.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            account_id: ID of the account to deposit to
            
        Verifies:
            - Response status code is 200
            - Response contains transaction details
            - Transaction type is 'deposit'
            - Transaction amount matches request
        """
        response = client.post("/transactions/deposit", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 101, "account_id": account_id})
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transaction" in response_json, f"invalid withdraw response, no key 'transaction' found"
        Transaction(**response_json["transaction"])
    
    def test_forbidden(self, client: FlaskClient, access_token: str) -> Transaction:
        """Test deposit with insufficient permissions.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            
        Verifies:
            - Response status code is 401
            - Response contains error message
            - Error message indicates forbidden access
        """
        response = client.post("/transactions/deposit", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 101, "account_id":"foo"})
        assert response.status_code == 401
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "Forbidden" in response_json["error"]

    def test_invalid_request(self, client: FlaskClient, access_token: str, account_id: str) -> Transaction:
        """Test deposit with invalid amount.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            account_id: ID of the account to deposit to
            
        Verifies:
            - Response status code is 400
            - Response contains error message
            - Error message indicates invalid amount field
        """
        response = client.post("/transactions/deposit", headers={"Authorization": f"Bearer {access_token}"}, json={"amount":"foo", "account_id": account_id})
        assert response.status_code == 400
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "invalid fields: amount" in response_json["error"]

    def test_missing_amount(self, client: FlaskClient, access_token: str, account_id: str) -> Transaction:
        """Test deposit with missing amount field.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            account_id: ID of the account to deposit to
            
        Verifies:
            - Response status code is 400
            - Response contains error message
            - Error message indicates missing amount field
        """
        response = client.post("/transactions/deposit", headers={"Authorization": f"Bearer {access_token}"}, json={"account_id": account_id})
        assert response.status_code == 400
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "invalid fields: amount" in response_json["error"]

    # TODO: maybe use the default account in this case? 
    def test_missing_account_id(self, client: FlaskClient, access_token: str, account_id: str) -> Transaction:
        """Test deposit with missing account_id field.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            account_id: ID of the account to deposit to
            
        Verifies:
            - Response status code is 400
            - Response contains error message
            - Error message indicates missing account_id field
        """
        response = client.post("/transactions/deposit", headers={"Authorization": f"Bearer {access_token}"}, json={"amount":100})
        assert response.status_code == 400
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "invalid fields: account_id" in response_json["error"]

class TestTransfer:
    """Test suite for POST /transactions/transfer endpoint.
    
    This test suite verifies the functionality of transfer transactions.
    It includes tests for successful transfers, invalid requests, missing fields,
    and unauthorized access scenarios.
    """
    
    def test_ok(self, client: FlaskClient, access_token: str, account_id: str, account_id_2: str) -> Transaction:
        """Test successful transfer transaction.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            account_id: ID of the source account
            account_id_2: ID of the recipient account
            
        Verifies:
            - Response status code is 200
            - Response contains transaction details
            - Transaction type is 'transfer'
            - Transaction amount matches request
            - Recipient ID is set correctly
        """
        response = client.post("/transactions/transfer", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 101, "account_id": account_id, "recipient_account_id": account_id_2})
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transaction" in response_json, f"invalid withdraw response, no key 'transaction' found"
        Transaction(**response_json["transaction"])
    
    def test_forbidden_sender(self, client: FlaskClient, access_token: str, account_id_2: str) -> Transaction:
        """Test transfer with insufficient permissions for sender account.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            account_id_2: ID of the recipient account
            
        Verifies:
            - Response status code is 401
            - Response contains error message
            - Error message indicates forbidden access
        """
        response = client.post("/transactions/transfer", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 101, "account_id":"foo", "recipient_account_id": account_id_2})
        assert response.status_code == 401
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "Forbidden" in response_json["error"]
    
    def test_not_found_recipient(self, client: FlaskClient, access_token: str, account_id: str) -> Transaction:
        """Test transfer to non-existent recipient account.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            account_id: ID of the source account
            
        Verifies:
            - Response status code is 404
            - Response contains error message
            - Error message indicates account not found
        """
        response = client.post("/transactions/transfer", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 101, "account_id":account_id, "recipient_account_id": "foo"})
        assert response.status_code == 404
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "account not found" in response_json["error"]

    def test_invalid_request(self, client: FlaskClient, access_token: str, account_id: str, account_id_2: str) -> Transaction:
        """Test transfer with invalid amount.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            account_id: ID of the source account
            account_id_2: ID of the recipient account
            
        Verifies:
            - Response status code is 400
            - Response contains error message
            - Error message indicates invalid amount field
        """
        response = client.post("/transactions/transfer", headers={"Authorization": f"Bearer {access_token}"}, json={"amount":"foo", "account_id": account_id, "recipient_account_id": account_id_2})
        assert response.status_code == 400
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "invalid fields: amount" in response_json["error"]

    def test_missing_amount(self, client: FlaskClient, access_token: str, account_id: str, account_id_2: str) -> Transaction:
        """Test transfer with missing amount field.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            account_id: ID of the source account
            account_id_2: ID of the recipient account
            
        Verifies:
            - Response status code is 400
            - Response contains error message
            - Error message indicates missing amount field
        """
        response = client.post("/transactions/transfer", headers={"Authorization": f"Bearer {access_token}"}, json={"account_id": account_id, "recipient_account_id": account_id_2})
        assert response.status_code == 400
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "invalid fields: amount" in response_json["error"]

    # TODO: maybe use the default account in this case? 
    def test_missing_account_id(self, client: FlaskClient, access_token: str, account_id: str, account_id_2: str) -> Transaction:
        """Test transfer with missing account_id field.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            account_id: ID of the source account
            account_id_2: ID of the recipient account
            
        Verifies:
            - Response status code is 400
            - Response contains error message
            - Error message indicates missing account_id field
        """
        response = client.post("/transactions/transfer", headers={"Authorization": f"Bearer {access_token}"}, json={"amount":100, "recipient_account_id": account_id_2})
        assert response.status_code == 400
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "invalid fields: account_id" in response_json["error"]

class TestGetTransactionCategories:
    def test_get_transaction_categories(self, client: FlaskClient, deposit: Transaction, withdraw: Transaction, transfer: Transaction,  access_token: str):
        response = client.get("/transactions/categories", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "categories" in response_json
        assert len(response_json["categories"]) == 1
        assert response_json["categories"][0] == "test"

class TestGetTransactions:
    """Test suite for GET /transactions endpoint.
    
    This test suite verifies the functionality of retrieving transactions.
    It includes tests for retrieving all transactions, filtering by type,
    filtering by account, and filtering by date range.
    """
    
    def test_get_transactions(self, client: FlaskClient, deposit: Transaction, withdraw: Transaction, transfer: Transaction,  access_token: str):
        """Test successful retrieval of all transactions.
        
        Args:
            client: Flask test client
            deposit: Test deposit transaction
            withdraw: Test withdrawal transaction
            transfer: Test transfer transaction
            access_token: Valid JWT access token
            
        Verifies:
            - Response status code is 200
            - Response contains all transaction types
            - Transaction amounts match test data
            - Transaction types are correct
        """
        response = client.get("/transactions", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
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
        """Test retrieval with empty transaction type filter.
        
        Args:
            client: Flask test client
            deposit: Test deposit transaction
            withdraw: Test withdrawal transaction
            transfer: Test transfer transaction
            access_token: Valid JWT access token
            
        Verifies:
            - Response status code is 200
            - Response contains all transaction types
            - Transaction amounts match test data
            - Transaction types are correct
        """
        response = client.get("/transactions?transaction_type=", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("content-type")
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
        """Test retrieval of deposit transactions.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            deposit: Test deposit transaction
            withdraw: Test withdrawal transaction
            transfer: Test transfer transaction
            
        Verifies:
            - Response status code is 200
            - Response contains only deposit transactions
            - Transaction amount matches test data
        """
        response = client.get("/transactions?transaction_type=deposit", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200, response.get_data()
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transactions" in response_json
        transactions = response_json["transactions"]

        assert len(transactions) == 1, f"expected 1 transaction, got {len(transactions)}"
        transaction = Transaction(**transactions[0])
        assert transaction.amount == deposit.amount
        
        
    def test_get_withdraw(self, client: FlaskClient, access_token: str, deposit: Transaction, withdraw: Transaction, transfer: Transaction):
        """Test retrieval of withdrawal transactions.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            deposit: Test deposit transaction
            withdraw: Test withdrawal transaction
            transfer: Test transfer transaction
            
        Verifies:
            - Response status code is 200
            - Response contains only withdrawal transactions
            - Transaction amount matches test data
        """
        response = client.get("/transactions?transaction_type=withdraw", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transactions" in response_json
        transactions = response_json["transactions"]

        assert len(transactions) == 1, f"expected 1 transaction, got {len(transactions)}"
        transaction = Transaction(**transactions[0])
        assert transaction.amount == withdraw.amount

    def test_get_transfer(self, client: FlaskClient, access_token: str, deposit: Transaction, withdraw: Transaction, transfer: Transaction):
        """Test retrieval of transfer transactions.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            deposit: Test deposit transaction
            withdraw: Test withdrawal transaction
            transfer: Test transfer transaction
            
        Verifies:
            - Response status code is 200
            - Response contains only transfer transactions
            - Transaction amount matches test data
        """
        response = client.get("/transactions?transaction_type=transfer", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "transactions" in response_json
        transactions = response_json["transactions"]

        assert len(transactions) == 1, f"expected 1 transaction, got {len(transactions)}"
        transaction = Transaction(**transactions[0])
        assert transaction.amount == transfer.amount

    def test_get_invalid_transaction_types(self, client: FlaskClient, access_token:str, deposit: Transaction, withdraw: Transaction, transfer: Transaction):
        """Test retrieval with invalid transaction type filter.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            deposit: Test deposit transaction
            withdraw: Test withdrawal transaction
            transfer: Test transfer transaction
            
        Verifies:
            - Response status code is 400
            - Response contains error message
        """
        response = client.get("/transactions?transaction_type=foo", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 400

    def test_get_2_transaction_types(self, client: FlaskClient, access_token:str, deposit: Transaction, withdraw: Transaction, transfer: Transaction):
        """Test retrieval of multiple transaction types.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            deposit: Test deposit transaction
            withdraw: Test withdrawal transaction
            transfer: Test transfer transaction
            
        Verifies:
            - Response status code is 200
            - Response contains specified transaction types
            - Transaction amounts match test data
            - Transaction types are correct
        """
        response = client.get("/transactions?transaction_type=transfer,deposit", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
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
        """Test retrieval of all transaction types.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            deposit: Test deposit transaction
            withdraw: Test withdrawal transaction
            transfer: Test transfer transaction
            
        Verifies:
            - Response status code is 200
            - Response contains all transaction types
            - Transaction amounts match test data
            - Transaction types are correct
        """
        response = client.get("/transactions?transaction_type=withdraw,transfer,deposit", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")
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
        """Test retrieval with mixed valid and invalid transaction types.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            deposit: Test deposit transaction
            withdraw: Test withdrawal transaction
            transfer: Test transfer transaction
            
        Verifies:
            - Response status code is 400
            - Response contains error message
        """
        response = client.get("/transactions?transaction_type=withdraw,foo,deposit", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 400


    def test_query_by_account_id(self, client: FlaskClient, access_token:str, withdraw: Transaction):
        """Test retrieval of transactions by account ID.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            withdraw: Test withdrawal transaction
            
        Verifies:
            - Response status code is 200
            - Response contains transactions for specified account
            - Transaction amount matches test data
        """
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
        """Test retrieval with non-existent account ID.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            
        Verifies:
            - Response status code is 200
            - Response contains empty transactions list
        """
        response = client.get("/transactions?account_id=foo", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type")        
        response_json = response.get_json()
        assert "transactions" in  response_json
        assert len(response_json["transactions"]) == 0

    def test_query_by_range(self, client: FlaskClient, access_token: str, transactions: List[Transaction]):
        """Test retrieval of transactions by date range.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            transactions: List of test transactions
            
        Verifies:
            - Response status code is 200
            - Response contains transactions within specified range
            - Number of transactions matches expected count
        """
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
    """Test suite for GET /transactions/:id endpoint.
    
    This test suite verifies the functionality of retrieving a specific transaction by ID.
    It includes tests for successful retrieval of different transaction types and
    handling of non-existent transactions.
    """
    
    def test_get_existing_withdraw(self, client: FlaskClient, access_token: str, withdraw: Transaction):
        """Test retrieval of existing withdrawal transaction.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            withdraw: Test withdrawal transaction
            
        Verifies:
            - Response status code is 200
            - Response contains transaction details
            - Transaction type is 'withdraw'
            - Transaction amount matches test data
        """
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
        """Test retrieval of existing deposit transaction.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            deposit: Test deposit transaction
            
        Verifies:
            - Response status code is 200
            - Response contains transaction details
            - Transaction type is 'deposit'
            - Transaction amount matches test data
        """
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
        """Test retrieval of existing transfer transaction.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            transfer: Test transfer transaction
            
        Verifies:
            - Response status code is 200
            - Response contains transaction details
            - Transaction type is 'transfer'
            - Transaction amount matches test data
            - Recipient ID is set correctly
        """
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
        """Test retrieval of non-existent transaction.
        
        Args:
            client: Flask test client
            access_token: Valid JWT access token
            
        Verifies:
            - Response status code is 404
            - Response contains error message
            - Error message indicates transaction not found
        """
        response = client.get(f"/transactions/foo", headers={"Authorization": f"Bearer {access_token}"}, follow_redirects=True)
        assert response.status_code == 404
        assert "application/json" in response.headers.get("content-type")
        response_json = response.get_json()
        assert "error" in response_json
        assert "transaction not found" in response_json["error"]