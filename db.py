import uuid
import logging
from datetime import datetime, timezone
from typing import TypeVar, Generic, Dict, Optional, Callable, List, Set
from pydantic import BaseModel, Field
from models import Transaction

# Set up logging for security audit
logging.basicConfig(level=logging.INFO)
security_logger = logging.getLogger("security")

T = TypeVar('T')
class Repository(Generic[T]):
    def __init__(self, collection: Dict):
        self.collection = collection
        # Fields that should never be updated directly
        self._protected_fields = {'id', 'created_at', 'updated_at'}
    
    # Add method to set custom protected fields for inheriting classes
    def set_protected_fields(self, fields: Set[str]):
        self._protected_fields.update(fields)
    
    def create(self, data: Dict) -> T:
        # Sanitize input data to prevent injection attacks
        data = self._sanitize_data(data)
        
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        else:
            # Check if the ID already exists to prevent overwrites
            if data['id'] in self.collection:
                raise ValueError(f"ID {data['id']} already exists in collection")
        
        now = datetime.now(timezone.utc).isoformat()
        data['created_at'] = now
        data['updated_at'] = now

        self.collection[data['id']] = data
        
        # Log creation for security audit
        security_logger.info(f"Created new record with ID {data['id']}")
        return data

    def find_by_id(self, id: str) -> Optional[T]:
        return self.collection.get(id)
    
    def find(self, filter_func: Optional[Callable[[T], bool]] = None) -> Optional[T]:
        if not filter_func:
            return None

        for value in self.collection.values():
            if filter_func(value):
                return value
            
        return None
    
    def find_all(self, filter_func: Optional[Callable[[T], bool]] = None) -> List[T]:
        values = list(self.collection.values())
        if filter_func:
            return list(filter(filter_func, values))
        return values
    
    def update(self, id: str, data: Dict) -> Optional[T]:
        """
        Update an entity by ID, with security protections:
        - Prevents updating protected fields
        - Sanitizes input data
        - Logs update attempts for security audit
        
        Args:
            id: The ID of the entity to update
            data: Dictionary containing the fields to update
            
        Returns:
            The updated entity or None if not found
            
        Raises:
            ValueError: If attempting to update protected fields
        """
        if id not in self.collection:
            security_logger.warning(f"Update attempt on non-existent ID: {id}")
            return None
        
        # Sanitize input data
        safe_data = self._sanitize_data(data)
        
        # Check for protected fields
        protected_fields_in_update = set(safe_data.keys()) & self._protected_fields
        if protected_fields_in_update:
            security_logger.warning(f"Attempt to update protected fields: {protected_fields_in_update} for ID {id}")
            raise ValueError(f"Cannot update protected fields: {protected_fields_in_update}")
        
        # Apply the update
        old_values = {k: self.collection[id].get(k) for k in safe_data if k in self.collection[id]}
        self.collection[id].update(safe_data)
        self.collection[id]['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        # Log for security audit
        security_logger.info(
            f"Updated ID {id}: Changed fields {list(safe_data.keys())}. "
            f"Old values: {old_values}, New values: {safe_data}"
        )
        
        return self.collection[id]
    
    def _sanitize_data(self, data: Dict) -> Dict:
        """
        Sanitize input data to prevent injection attacks
        
        This method should be extended based on specific needs
        """
        # Create a copy to avoid modifying the original
        sanitized = dict(data)
        
        # Basic sanitization - handle strings only
        for key, value in sanitized.items():
            if isinstance(value, str):
                # Remove potential script tags and escape special characters
                # This is a basic example - real implementation should be more thorough
                sanitized[key] = (
                    value.replace("<script>", "")
                    .replace("</script>", "")
                )
        
        return sanitized
    
    def delete(self, id: str) -> bool:
        if id not in self.collection:
            return False
        
        # Log deletion for security audit
        security_logger.info(f"Deleted record with ID {id}")
        
        del self.collection[id]
        return True
    
class UserRepository(Repository[Dict]):
    def find_by_email(self, email: str) -> Optional[Dict]:
        return self.find(lambda collection: collection["email"] == email)
    
class AccountRepository(Repository[Dict]):
    def find_by_user_id(self, user_id: str) -> List[Dict]:
        return self.find_all(lambda collection: collection["user_id"] == user_id)
    

class DateRange(BaseModel):
    start: Optional[datetime] = Field(None, description="Start date/time")
    end: Optional[datetime] = Field(None, description="End date/time")

    def is_in_range(self,created_at: str) -> bool:
        # sometime, the formatted string has Z timezone information
        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if self.start == None and self.end == None:
            return True
        
        if self.start == None:
            return dt <= self.end
        
        if self.end == None:
            return dt >= self.start
        
        return self.start <= dt <= self.end

class TransactionQuery(BaseModel):
    account_id: Optional[str] = Field(None, description="Optional filter by account ID")
    date_range: Optional[DateRange] = Field(None, description="Optional date_range")

    def filter(self, collection: Dict) -> bool:
        if not self.account_id == None and not collection["account_id"] == self.account_id:
            return False
        if not self.date_range == None and not self.date_range.is_in_range(collection["created_at"]):
            return False
        
        return True

class NewTransactionRequest(BaseModel):
    account_id: str
    transaction_type: str = Field("withdrawal", description="Transaction Type, either 'withdrawal', 'deposit', or 'transfer'")
    amount: int = Field(0, description="The amount of balance being affected by the transaction")
    sender_account: Optional[str] = Field(None, description="The account id of the sender, if the transaction type is 'transfer'")
    recipient_account: Optional[str] = Field(None, description="The account id of the recipient, if the transaction type is 'transfer'")

    def create_transaction(self, user_id: str) -> Transaction:
        transaction = Transaction()
        transaction.user_id = user_id
        transaction.account_id = self.account_id
        transaction.transaction_type = self.transaction_type
        transaction.amount = self.amount
        transaction.sender_account = self.sender_account
        transaction.recipient_account = self.recipient_account
        return transaction
class TransactionRepository(Repository[Dict]):    
    def find_by_user_id(self, user_id: str) -> List[Dict]:
        return self.find_all(lambda collection: collection["user_id"] == user_id)
    
    def query_transaction(self, user_id: str, query: TransactionQuery) -> List[Dict]:
        return filter(
            query.filter,
            self.find_by_user_id(user_id))