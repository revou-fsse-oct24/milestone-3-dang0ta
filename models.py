from pydantic import BaseModel, EmailStr, Field

class UserInformation(BaseModel):
    name: str = Field(..., description="The name of the user")
    email: EmailStr = Field(..., description="The email address of the user")

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