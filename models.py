from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_serializer
from enum import Enum
from datetime import datetime
from typing import Optional, List

class UserInformation(BaseModel):
    name: str = Field(..., description="The name of the user")
    fullname: str | None = Field(None, description="The full name of the user")
    email_address: EmailStr = Field(..., description="The email address of the user")
    default_account: Optional["Account"] = Field(None, description="The default account of the user")
    roles: List[str] = Field(["customer"], description="The list of roles the user assumes")
    accounts: List["Account"] = Field([], description="The list of accounts the user has")

# TODO: delete UserCredential class
class UserCredential(UserInformation):    
    password: str

    def info(self) ->UserInformation:
        return UserInformation(
            name=self.name,
            fullname=self.fullname,
            email_address=self.email_address
        )
    
class CreateUserRequest(BaseModel):
    name: str = Field(..., description="The name of the user")
    fullname: str | None = Field(None, description="The full name of the user")
    email_address: EmailStr = Field(..., description="The email address of the user")
    password: str = Field(..., description="user's password for authentication")
    roles: List[str] = Field(["customer"], description="the list of roles the user will assume")

class Account(BaseModel):
    id: str
    user_id: str
    balance: int
    created_at: datetime
    updated_at: datetime

    # there's a strange interaction for sqlalchemy's model and pydantic's model when dealing
    # with datetime. sqlalchemy serializes its own DateTime into human-readable format like 
    # 'Fri, April 4th, 2025 ....' and they're not parseable by pydantic. Pydantic also seems to 
    # do this, so when serializing the model with model_dump(), and then turning it back into 
    # model class with 'Model(**response)' it gives parsing error on the datetime. I'm probably
    # missing something on this, but this is the current working aproach that I can find for 
    # safely serialize and deserialize datetime between pydantic and sqlalchemy model. Notice
    # that I'm also calling '.isoformat()' on `to_model()` method on sqlalchemy models.
    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime, _info):
        return created_at.isoformat()
    
    @field_serializer('updated_at') 
    def serialize_updated_at(self, updated_at: datetime, _info):
        return updated_at.isoformat()
class CreateAccountRequest(BaseModel):
    balance: int

class UpdateAccountRequest(BaseModel):
    account_id: str | None = Field(None, description="the ID of the account that will be updated, if not set, the user's default account will be updated instead")
    balance: int = Field(..., description="the balance change that will be applied to the account")
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
