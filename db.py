import uuid
from datetime import datetime, timezone
from typing import TypeVar, Generic, Dict, Optional, Callable, List

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
        for user in self.collection.values():
            if user['email'] == email:
                return user
        return None