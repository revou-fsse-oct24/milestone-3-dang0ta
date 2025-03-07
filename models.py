from pydantic import BaseModel

class UserInformation(BaseModel):
    name: str
    email: str

class UserCredential(UserInformation):    
    password: str

class Account(BaseModel):
    user_id: str
    balance: int

