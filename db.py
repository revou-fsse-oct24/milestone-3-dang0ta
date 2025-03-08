import uuid
from datetime import datetime, timezone
from typing import TypeVar, Generic, Dict, Optional, Callable, List
from pydantic import BaseModel, Field
from models import Transaction

T = TypeVar('T')
class Repository(Generic[T]):
    def __init__(self, collection: Dict):
        self.collection = collection
    
    def create(self, data: Dict) -> T:
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        
        now = datetime.now(timezone.utc).isoformat()
        data['created_at'] = now
        data['updated_at'] = now

        self.collection[data['id']] = data
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
        if id not in self.collection:
            return None
        
        self.collection[id].update(data)
        self.collection[id]['updated_at'] = datetime.now(timezone.utc).isoformat()
        return self.collection[id]
    
    def delete(self, id: str) -> bool:
        if id not in self.collection:
            return False
        
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