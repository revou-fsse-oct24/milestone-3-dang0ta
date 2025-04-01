from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_serializer
from enum import Enum
from datetime import datetime
from typing import Optional

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

class TransactionTypes(str, Enum):
    model_config = ConfigDict(use_enum_values=True)
    withdraw = "withdraw"
    deposit = "deposit"
    transfer = "transfer"

class Transaction(BaseModel):
    id: str = Field(..., description="The ID of the transaction")
    account_id: str = Field(..., description="The ID of the current user's account")
    transaction_type: TransactionTypes = Field(..., description="either 'withdraw', 'deposit' or 'transfer'")
    amount: int = Field(..., description="the nominal of the transfer, accepts only positive number if transfer_type is 'withdraw' or 'deposit'. Negative number on transaction_type transfer indicates transfer from account_id to recipient_account_id, positive number indicates otherwise")
    timestamp: datetime = Field(..., description="the timestamp of the transaction")
    recipient_id: Optional[str] = Field(None, description="only set if transaction_type is transfer, the account id of the transfer recipient")

    @field_serializer('timestamp')
    def serialize_timestamp(self, timestamp: datetime, _info):
        return timestamp.isoformat()



class WithdrawRequest(BaseModel):
    account_id: str = Field(..., description="The ID of the current user's account")
    amount: int = Field(..., description="the nominal of the transfer, accepts only positive number if transfer_type is 'withdraw' or 'deposit'. Negative number on transaction_type transfer indicates transfer from account_id to recipient_account_id, positive number indicates otherwise")

class DepositRequest(BaseModel):
    account_id: str = Field(..., description="The ID of the current user's account")
    amount: int = Field(..., description="the nominal of the transfer, accepts only positive number if transfer_type is 'withdraw' or 'deposit'. Negative number on transaction_type transfer indicates transfer from account_id to recipient_account_id, positive number indicates otherwise")

class TransferRequest(BaseModel):
    account_id: str = Field(..., description="The ID of the current user's account")
    recipient_account_id: str = Field(..., description="The ID of the recipient account")
    amount: int = Field(..., description="the nominal of the transfer, accepts only positive number if transfer_type is 'withdraw' or 'deposit'. Negative number on transaction_type transfer indicates transfer from account_id to recipient_account_id, positive number indicates otherwise")
