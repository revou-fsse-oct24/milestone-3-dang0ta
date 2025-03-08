from pydantic import BaseModel

class UserInformation(BaseModel):
    name: str
    email: str

class UserCredential(UserInformation):    
    password: str

class Account(BaseModel):
    user_id: str
    balance: int



class Transaction(BaseModel):
    user_id: str
    account_id: str
    transaction_type: str
    amount: int
    sender_account: str | None
    recipient_account: str | None