from pydantic import BaseModel, EmailStr, Field

class UserInformation(BaseModel):
    name: str = Field(..., description="The name of the user")
    fullname: str | None = Field(None, description="The full name of the user")
    email_address: EmailStr = Field(..., description="The email address of the user")

class UserCredential(UserInformation):    
    password: str

    def info(self) ->UserInformation:
        return UserInformation(
            name=self.name,
            fullname=self.fullname,
            email_address=self.email_address
        )

class Account(BaseModel):
    balance: int

class Transaction(BaseModel):
    account_id: str = Field(..., description="The ID of the current user's account")
    recipient_account_id: str | None = Field(None, description="set only if transaction_type is 'transfer', this is the account ID of the recipient account")
    transaction_type: str = Field(..., description="either 'withdraw', 'deposit' or 'transfer'")
    amount: int = Field(..., description="the nominal of the transfer, accepts only positive number if transfer_type is 'withdraw' or 'deposit'. Negative number on transaction_type transfer indicates transfer from account_id to recipient_account_id, positive number indicates otherwise")