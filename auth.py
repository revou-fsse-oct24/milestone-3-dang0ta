import bcrypt
from typing import Optional

class Hash:
    def __init__(self, user_id:str, password:str):
        self.user_id = user_id
        self.hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    def compare(self, password: str) -> bool:
        return bcrypt.checkpw(password=password.encode(), hashed_password=self.hash)
    

class UserNotFoundException(Exception):
    # keep the email for logging
    email: str
    def __init__(self, email: str):
        super().__init__("the given user credential is not found")
        self.email = email

class WrongCredentialException(Exception):
    # keep the email for logging
    email: str
    def __init__(self, email):
        super().__init__("incorrect email/password")
        self.email = email

class AuthRepository:
    def __init__(self, *, users: dict = None):
        self.users = users or {}
    
    def register(self, email: str, password: str, user_id: str):
        self.users[email] = Hash(user_id=user_id, password=password)
            
    def authenticate(self, email: str, password: str) -> Optional[str]:
        if email is None or password is None:
            raise WrongCredentialException(email)
        if email not in self.users:
            raise UserNotFoundException(email)
        if self.users[email].compare(password):
            return self.users[email].user_id
        else:
            raise WrongCredentialException(email)
