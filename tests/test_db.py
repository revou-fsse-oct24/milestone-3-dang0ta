import pytest
from datetime import datetime, timedelta
from db import Repository, UserRepository, AccountRepository, TransactionRepository, DateRange, TransactionQuery, NewTransactionRequest
from models import Transaction

@pytest.fixture
def sample_collection():
    """Fixture to provide a sample collection for testing."""
    return {
        "1": {
            "id": "1",
            "name": "Test Item 1",
            "created_at": "2023-01-01T00:00:00+00:00",
            "updated_at": "2023-01-01T00:00:00+00:00"
        },
        "2": {
            "id": "2",
            "name": "Test Item 2",
            "created_at": "2023-01-02T00:00:00+00:00",
            "updated_at": "2023-01-02T00:00:00+00:00"
        }
    }

@pytest.fixture
def repo(sample_collection):
    """Fixture to provide a Repository instance for testing."""
    return Repository(sample_collection)

def test_create_with_id(repo):
    """Test creating an item with a specified ID."""
    data = {"id": "3", "name": "Test Item 3"}
    result = repo.create(data)
    
    assert result["id"] == "3"
    assert result["name"] == "Test Item 3"
    assert "created_at" in result
    assert "updated_at" in result
    assert repo.collection["3"] == result

def test_create_without_id(repo):
    """Test creating an item without specifying an ID."""
    data = {"name": "Test Item Auto ID"}
    result = repo.create(data)
    
    assert "id" in result
    assert len(result["id"]) > 0
    assert result["name"] == "Test Item Auto ID"
    assert "created_at" in result
    assert "updated_at" in result
    assert repo.collection[result["id"]] == result

def test_find_by_id_existing(repo):
    """Test finding an item by ID when it exists."""
    result = repo.find_by_id("1")
    
    assert result is not None
    assert result["name"] == "Test Item 1"

def test_find_by_id_non_existing(repo):
    """Test finding an item by ID when it doesn't exist."""
    result = repo.find_by_id("999")
    
    assert result is None

def test_find_all_no_filter(repo):
    """Test finding all items without a filter."""
    results = repo.find_all()
    
    assert len(results) == 2
    assert any(item["id"] == "1" for item in results)
    assert any(item["id"] == "2" for item in results)

def test_find_all_with_filter(repo):
    """Test finding items with a filter function."""
    results = repo.find_all(lambda item: item["name"] == "Test Item 1")
    
    assert len(results) == 1
    assert results[0]["id"] == "1"

def test_update_existing(repo):
    """Test updating an existing item."""
    orig_updated_at = repo.collection["1"]["updated_at"]
    result = repo.update("1", {"name": "Updated Item"})
    
    assert result is not None
    assert result["name"] == "Updated Item"
    assert result["updated_at"] != orig_updated_at
    assert repo.collection["1"]["name"] == "Updated Item"

def test_update_non_existing(repo):
    """Test updating a non-existing item."""
    result = repo.update("999", {"name": "This Won't Work"})
    
    assert result is None
    assert "999" not in repo.collection

def test_delete_existing(repo):
    """Test deleting an existing item."""
    result = repo.delete("1")
    
    assert result is True
    assert "1" not in repo.collection

def test_delete_non_existing(repo):
    """Test deleting a non-existing item."""
    result = repo.delete("999")
    
    assert result is False

def test_find_method(repo):
    """Test the find method with a filter function."""
    result = repo.find(lambda item: item["name"] == "Test Item 1")
    
    assert result is not None
    assert result["id"] == "1"
    assert result["name"] == "Test Item 1"

def test_find_method_no_match(repo):
    """Test the find method when no items match."""
    result = repo.find(lambda item: item["name"] == "Non-existent Item")
    
    assert result is None

def test_find_method_none_filter(repo):
    """Test the find method with None as filter."""
    result = repo.find(None)
    
    assert result is None

def test_sanitize_data(repo):
    """Test the _sanitize_data method."""
    dirty_data = {
        "name": "Test <script>alert('XSS')</script> Item",
        "number": 42
    }
    
    clean_data = repo._sanitize_data(dirty_data)
    
    assert clean_data["name"] == "Test alert('XSS') Item"
    assert clean_data["number"] == 42

def test_protected_fields(repo):
    """Test that protected fields cannot be updated."""
    with pytest.raises(ValueError) as excinfo:
        repo.update("1", {"id": "changed_id", "name": "Valid Change"})
    
    assert "Cannot update protected fields" in str(excinfo.value)
    assert repo.collection["1"]["id"] == "1"
    assert repo.collection["1"]["name"] == "Test Item 1"

def test_set_protected_fields():
    """Test setting custom protected fields."""
    collection = {"1": {"id": "1", "name": "Test", "custom_field": "value"}}
    repo = Repository(collection)
    repo.set_protected_fields({"custom_field"})
    
    with pytest.raises(ValueError) as excinfo:
        repo.update("1", {"custom_field": "new_value"})
    
    assert "Cannot update protected fields" in str(excinfo.value)
    assert "custom_field" in str(excinfo.value)
    assert collection["1"]["custom_field"] == "value"

@pytest.fixture
def user_collection():
    return {
        "1": {
            "id": "1", 
            "name": "Test User",
            "email": "test@example.com",
            "created_at": "2023-01-01T00:00:00+00:00",
            "updated_at": "2023-01-01T00:00:00+00:00"
        },
        "2": {
            "id": "2", 
            "name": "Another User",
            "email": "another@example.com",
            "created_at": "2023-01-02T00:00:00+00:00",
            "updated_at": "2023-01-02T00:00:00+00:00"
        }
    }

@pytest.fixture
def user_repo(user_collection):
    return UserRepository(user_collection)

def test_user_repo_find_by_email(user_repo):
    """Test UserRepository find_by_email method."""
    result = user_repo.find_by_email("test@example.com")
    
    assert result is not None
    assert result["id"] == "1"
    assert result["name"] == "Test User"
    
    # Test with non-existing email
    result = user_repo.find_by_email("nonexistent@example.com")
    assert result is None

@pytest.fixture
def account_collection():
    return {
        "1": {
            "id": "1",
            "user_id": "1",
            "balance": 1000,
            "created_at": "2023-01-01T00:00:00+00:00",
            "updated_at": "2023-01-01T00:00:00+00:00"
        },
        "2": {
            "id": "2",
            "user_id": "1",
            "balance": 500,
            "created_at": "2023-01-02T00:00:00+00:00",
            "updated_at": "2023-01-02T00:00:00+00:00"
        },
        "3": {
            "id": "3",
            "user_id": "2",
            "balance": 2000,
            "created_at": "2023-01-03T00:00:00+00:00",
            "updated_at": "2023-01-03T00:00:00+00:00"
        }
    }

@pytest.fixture
def account_repo(account_collection):
    return AccountRepository(account_collection)

def test_account_repo_find_by_user_id(account_repo):
    """Test AccountRepository find_by_user_id method."""
    results = account_repo.find_by_user_id("1")
    
    assert len(results) == 2
    assert results[0]["id"] in ["1", "2"]
    assert results[1]["id"] in ["1", "2"]
    
    # Test with user having one account
    results = account_repo.find_by_user_id("2")
    assert len(results) == 1
    assert results[0]["id"] == "3"
    
    # Test with non-existing user
    results = account_repo.find_by_user_id("3")
    assert len(results) == 0

# def test_date_range():
#     """Test DateRange is_in_range method."""
#     now = datetime.now()
#     yesterday = now - timedelta(days=1)
#     tomorrow = now + timedelta(days=1)
    
#     # Create ISO format strings
#     now_str = now.isoformat()
#     yesterday_str = yesterday.isoformat()
#     tomorrow_str = tomorrow.isoformat()
    
#     # Test with both start and end
#     date_range = DateRange(start=yesterday, end=tomorrow)
#     assert date_range.is_in_range(now_str) == True
#     assert date_range.is_in_range(yesterday_str) == True
#     assert date_range.is_in_range(tomorrow_str) == True
    
#     # Test with only start
#     date_range = DateRange(start=now)
#     assert date_range.is_in_range(now_str) == True
#     assert date_range.is_in_range(yesterday_str) == False
#     assert date_range.is_in_range(tomorrow_str) == True
    
#     # Test with only end
#     date_range = DateRange(end=now)
#     assert date_range.is_in_range(now_str) == True
#     assert date_range.is_in_range(yesterday_str) == True
#     assert date_range.is_in_range(tomorrow_str) == False
    
#     # Test with no bounds
#     date_range = DateRange()
#     assert date_range.is_in_range(now_str) == True
#     assert date_range.is_in_range(yesterday_str) == True
#     assert date_range.is_in_range(tomorrow_str) == True
    
#     # Test with Z timezone format
#     date_range = DateRange(start=yesterday, end=tomorrow)
#     assert date_range.is_in_range(now_str + "Z") == True

def test_transaction_query_filter():
    """Test TransactionQuery filter method."""
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    tomorrow = now + timedelta(days=1)
    
    collection = {
        "account_id": "1",
        "created_at": now.isoformat()
    }
    
    # Test with matching account_id
    query = TransactionQuery(account_id="1")
    assert query.filter(collection) == True
    
    # Test with non-matching account_id
    query = TransactionQuery(account_id="2")
    assert query.filter(collection) == False
    
    # Test with matching date range
    query = TransactionQuery(
        date_range=DateRange(start=yesterday, end=tomorrow)
    )
    assert query.filter(collection) == True
    
    # Test with non-matching date range
    query = TransactionQuery(
        date_range=DateRange(start=tomorrow, end=tomorrow + timedelta(days=1))
    )
    assert query.filter(collection) == False
    
    # Test with both account_id and date range
    query = TransactionQuery(
        account_id="1",
        date_range=DateRange(start=yesterday, end=tomorrow)
    )
    assert query.filter(collection) == True
    
    query = TransactionQuery(
        account_id="2",
        date_range=DateRange(start=yesterday, end=tomorrow)
    )
    assert query.filter(collection) == False

def test_new_transaction_request():
    """Test NewTransactionRequest create_transaction method."""
    # This requires mocking the Transaction class
    class MockTransaction:
        def __init__(self):
            self.user_id = None
            self.account_id = None
            self.transaction_type = None
            self.amount = None
            self.sender_account = None
            self.recipient_account = None
    
    # Temporarily replace Transaction with MockTransaction for the test
    import db
    original_transaction = db.Transaction
    db.Transaction = MockTransaction
    
    try:
        request = NewTransactionRequest(
            account_id="1",
            transaction_type="deposit",
            amount=100
        )
        
        # Create a transaction
        transaction = request.create_transaction("user1")
        
        # Check all fields were set correctly
        assert transaction.user_id == "user1"
        assert transaction.account_id == "1"
        assert transaction.transaction_type == "deposit"
        assert transaction.amount == 100
        assert transaction.sender_account is None
        assert transaction.recipient_account is None
        
        # Test with transfer type
        request = NewTransactionRequest(
            account_id="2",
            transaction_type="transfer",
            amount=200,
            sender_account="1",
            recipient_account="3"
        )
        
        transaction = request.create_transaction("user1")
        
        assert transaction.user_id == "user1"
        assert transaction.account_id == "2"
        assert transaction.transaction_type == "transfer"
        assert transaction.amount == 200
        assert transaction.sender_account == "1"
        assert transaction.recipient_account == "3"
        
    finally:
        # Restore original Transaction class
        db.Transaction = original_transaction

@pytest.fixture
def transaction_collection():
    return {
        "1": {
            "id": "1",
            "user_id": "1",
            "account_id": "1",
            "transaction_type": "deposit",
            "amount": 100,
            "created_at": "2023-01-01T00:00:00+00:00",
            "updated_at": "2023-01-01T00:00:00+00:00"
        },
        "2": {
            "id": "2",
            "user_id": "1",
            "account_id": "2",
            "transaction_type": "withdrawal",
            "amount": 50,
            "created_at": "2023-01-02T00:00:00+00:00",
            "updated_at": "2023-01-02T00:00:00+00:00"
        },
        "3": {
            "id": "3",
            "user_id": "2",
            "account_id": "3",
            "transaction_type": "deposit",
            "amount": 200,
            "created_at": "2023-01-03T00:00:00+00:00",
            "updated_at": "2023-01-03T00:00:00+00:00"
        }
    }

@pytest.fixture
def transaction_repo(transaction_collection):
    return TransactionRepository(transaction_collection)

def test_transaction_repo_find_by_user_id(transaction_repo):
    """Test TransactionRepository find_by_user_id method."""
    results = transaction_repo.find_by_user_id("1")
    
    assert len(results) == 2
    assert results[0]["id"] in ["1", "2"]
    assert results[1]["id"] in ["1", "2"]
    
    results = transaction_repo.find_by_user_id("2")
    assert len(results) == 1
    assert results[0]["id"] == "3"
    
    results = transaction_repo.find_by_user_id("3")
    assert len(results) == 0

def test_transaction_repo_query_transaction(transaction_repo):
    """Test TransactionRepository query_transaction method."""
    # Query by account_id
    query = TransactionQuery(account_id="1")
    results = list(transaction_repo.query_transaction("1", query))
    
    assert len(results) == 1
    assert results[0]["id"] == "1"
    
    # Query by date range
    start_date = datetime.fromisoformat("2023-01-01T00:00:00+00:00")
    end_date = datetime.fromisoformat("2023-01-02T00:00:00+00:00")
    query = TransactionQuery(date_range=DateRange(start=start_date, end=end_date))
    results = list(transaction_repo.query_transaction("1", query))
    
    assert len(results) == 2
    assert results[0]["id"] in ["1", "2"]
    assert results[1]["id"] in ["1", "2"]
    
    # Query with both filters
    query = TransactionQuery(
        account_id="2",
        date_range=DateRange(start=start_date, end=end_date)
    )
    results = list(transaction_repo.query_transaction("1", query))
    
    assert len(results) == 1
    assert results[0]["id"] == "2"
    
    # Query with no matching results
    query = TransactionQuery(account_id="999")
    results = list(transaction_repo.query_transaction("1", query))
    
    assert len(results) == 0
