from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_serializer, PlainSerializer
from enum import Enum
from datetime import datetime, timezone
from typing import Optional, List, Annotated
import zoneinfo

DateTime = Annotated[
    # SQLite doesn't store any timezone information, so we assume everything coming from them is in UTC, see unit testing.
    # we need to do integration test with real PostgreSQL to ensure that the test works well.
    datetime, PlainSerializer(lambda dt: dt.replace(tzinfo=zoneinfo.ZoneInfo("UTC")).isoformat())
]

class UserInformation(BaseModel):
    name: str = Field(..., description="The name of the user")
    fullname: str | None = Field(None, description="The full name of the user")
    email_address: EmailStr = Field(..., description="The email address of the user")
    default_account: Optional["Account"] = Field(None, description="The default account of the user")
    roles: List[str] = Field(["customer"], description="The list of roles the user assumes")
    accounts: List["Account"] = Field([], description="The list of accounts the user has")
    budgets: List["Budget"] = Field([], description="The list of the user's budget")

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
    category: str = Field(..., description="the category of the transaction")

    @field_serializer('timestamp')
    def serialize_timestamp(self, timestamp: datetime, _info):
        return timestamp.isoformat()


class TransactionRequest(BaseModel):
    account_id: str = Field(..., description="The ID of the current user's account")
    amount: int = Field(..., description="the nominal of the transfer, accepts only positive number if transfer_type is 'withdraw' or 'deposit'. Negative number on transaction_type transfer indicates transfer from account_id to recipient_account_id, positive number indicates otherwise")
    description: str | None = Field(None, description="description about the transaction")
    category: str = Field("none", description="the category of the transaction")
class WithdrawRequest(TransactionRequest):
    pass

class DepositRequest(TransactionRequest):
    pass

class TransferRequest(TransactionRequest):
    recipient_account_id: str = Field(..., description="The ID of the recipient account")

class CreateBudgetRequest(BaseModel):
    name: str = Field(..., description="The name for the budget")
    amount: int = Field(..., description="The limit of the budget")
    start_date: DateTime = Field(..., description="Budget's start date")
    end_date: DateTime = Field(..., description="Budget's end date")

class UpdateBudgetRequest(BaseModel):
    name: Optional[str] = Field(None, description="The name for the budget")
    amount: Optional[int] = Field(None, description="The limit of the budget")
    start_date: Optional[DateTime] = Field(None, description="Budget's start date")
    end_date: Optional[DateTime] = Field(None, description="Budget's end date")

class Budget(BaseModel):
    id: str = Field(..., description="The ID of the budget")
    user: Optional[UserInformation] = Field(None, description="The owner of the budget")
    name: str = Field(..., description="The name of the budget")
    amount: int = Field(..., description="The limit of the budget")
    start_date: DateTime = Field(..., description="The budget's start date")
    end_date: DateTime = Field(..., description="The budget's end date")


class CreateBillRequest(BaseModel):
    account_id: str | None = Field(None, description="the id of the account where the bill is assigned to")
    biller_name: str = Field(..., description="the name of the biller")
    due_date: DateTime = Field(..., description="the due date of the bill")
    amount: int = Field(..., description="payment amount")

class QueryBillsRequest(BaseModel):
    account_id: str | None = Field(None, description="filter the bills based on the account ID")
    biller_name: str | None = Field(None, description="filter the bills based on the biller name")
    due_date_from: DateTime | None = Field(None, description="set the start date for filtering the bills based on certain range of due date")
    due_date_to: DateTime | None = Field(None, description="set the end date for filtering the bills based on certain range of due date")
    amount_min: int | None = Field(None, description="set the min value for filtering the bills based on the range of the bill's payment amount")
    amount_max: int | None = Field(None, description="set the max value for filtering the bills based on the range of the bill's payment amount")

class UpdateBillRequest(BaseModel):
    biller_name: str | None = Field(None, description="change the biller name")
    due_date: DateTime | None = Field(None, description="change the due date")
    amount: int | None = Field(None, description="change the amount")

class Bill(BaseModel):
    id: str = Field(..., description="unique identifier of the bill")
    account_id: str = Field(..., description="the id of the account where the bill is assigned to")
    biller_name: str = Field(..., description="the name of the biller")
    due_date: DateTime = Field(..., description="the due date of the bill")
    amount: int = Field(..., description="payment amount")