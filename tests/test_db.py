import pytest
from db import Repository

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
