from typing import Optional, List
from db import db_session, Accounts, Transactions, TransactionEntries, TransactionCategories
from models import Transaction as TransactionModel, TransactionTypes, DepositRequest, WithdrawRequest, TransferRequest
from .accounts import AccountNotFoundException
from sqlalchemy import select
from sqlalchemy.orm import joinedload 
from pydantic import BaseModel
from datetime import datetime

class TransactionNotFoundException(Exception):
    def __init__(self, *, transaction_id:str):
        super().__init__("transaction not found")
        self.transaction_id = transaction_id


def withdraw(request=WithdrawRequest) -> Optional[TransactionModel]:
    account = db_session.get(Accounts, request.account_id)
    if account is None:
        raise AccountNotFoundException(account_id=request.account_id)
    
    account.balance = account.balance - request.amount
    transaction = Transactions(
        transaction_type="withdraw",
        description=request.description,
    )

    db_session.add(transaction)
    db_session.flush()

    entry = TransactionEntries(
        transaction_id = transaction.id,
        account_id = account.id,
        entry_type = "debit",
        amount = request.amount
    )
    
    category = TransactionCategories(
        name=request.category,
        transaction_id=transaction.id
    )

    db_session.add_all([entry, category])
    db_session.flush()
    db_session.commit()
    return TransactionModel(
        id=str(transaction.id),
        account_id=str(account.id),
        transaction_type=transaction.transaction_type,
        amount=request.amount,
        timestamp=transaction.timestamp.isoformat(),
        category=category.name,
    )

def deposit(request: DepositRequest) -> Optional[TransactionModel]:    
    account = db_session.get(Accounts, request.account_id)
    if account is None:
        raise AccountNotFoundException(account_id=request.account_id)
    
    account.balance = account.balance + request.amount
    transaction = Transactions(
        transaction_type="deposit",
        description=request.description,
    )

    db_session.add(transaction)
    db_session.flush()

    entry = TransactionEntries(
        transaction_id = transaction.id,
        account_id = account.id,
        entry_type = "credit",
        amount=request.amount
    )

    category=TransactionCategories(
        name=request.category,
        transaction_id=transaction.id
    )
    
    db_session.add_all([entry, category])
    db_session.commit()
    return TransactionModel(
        id=str(transaction.id),
        account_id=str(account.id),
        transaction_type=transaction.transaction_type,
        amount=request.amount,
        timestamp=transaction.timestamp.isoformat(),
        category=category.name,
    )

def transfer(request: TransferRequest) -> Optional[TransactionModel]:
    sender_account = db_session.get(Accounts, request.account_id)
    if sender_account is None:
        raise AccountNotFoundException(account_id=request.account_id)
    
    recipient_account = db_session.get(Accounts, request.recipient_account_id)
    if recipient_account is None:
        raise AccountNotFoundException(account_id=request.recipient_account_id)

    sender_account.balance = sender_account.balance - request.amount
    recipient_account.balance = recipient_account.balance + request.amount

    transaction = Transactions(
        transaction_type="transfer", 
        description=request.description,
    )

    db_session.add(transaction)
    db_session.flush()

    sender_entry = TransactionEntries(
        transaction_id = transaction.id,
        account_id = sender_account.id,
        entry_type = "debit",
        amount = request.amount
    )

    recipient_entry = TransactionEntries(
        transaction_id = transaction.id,
        account_id = recipient_account.id,
        entry_type = "credit",
        amount = request.amount
    )

    category = TransactionCategories(
        name=request.category,
        transaction_id=transaction.id,
    )

    db_session.add_all([sender_entry, recipient_entry, category])
    db_session.commit()
    return TransactionModel(
        id=str(transaction.id),
        account_id=str(sender_account.id),
        transaction_type=transaction.transaction_type,
        amount=sender_entry.amount,
        timestamp=transaction.timestamp.isoformat(),
        recipient_id=str(recipient_entry.account_id),
        category=category.name
    )
class TransactionQuery(BaseModel):
    account_id: Optional[str] = None
    range_from: Optional[datetime]  = None
    range_to: Optional[datetime] = None
    transaction_type: Optional[List[TransactionTypes]] = None
    
def get_transactions(query: TransactionQuery, current_user: str) -> List[TransactionModel]:
    statement= (
        select(
            Transactions
        )
        .select_from(TransactionEntries)
        .join(Accounts)
        .join(Transactions)
        .where(Accounts.user_id.is_(current_user))
        .options(joinedload(Transactions.entries))
        .options(joinedload(Transactions.category))
    )
    
    if query.account_id is not None:
        statement = statement.filter(Accounts.id.is_(query.account_id))
    if query.range_from is not None:
        statement = statement.filter(Transactions.timestamp >= query.range_from)
    if query.range_to is not None:
        statement = statement.filter(Transactions.timestamp <= query.range_to)
    if query.transaction_type is not None:
        statement = statement.filter(Transactions.transaction_type.in_(query.transaction_type))
        
    result = db_session.scalars(statement=statement).unique().all()
    transactions: List[TransactionModel] = []
    for transaction in result:
        parsed = _parse_transaction_model(transaction)
        if parsed is not None:
            transactions.append(parsed)

    return transactions
    
def get_transaction(transaction_id:str) -> Optional[TransactionModel]:
    transaction = db_session.get(Transactions, transaction_id, options=[joinedload(Transactions.entries), joinedload(Transactions.category)])

    if transaction is None:
        raise TransactionNotFoundException(transaction_id=transaction_id)

    result = _parse_transaction_model(transaction)
    if result is None:
        raise TransactionNotFoundException(transaction_id=transaction_id)
    
    return result
        
    
def _parse_transaction_model(transaction: Transactions)-> Optional[TransactionModel]:
    if len(transaction.entries) == 0:
        # TODO: log out that there's an invalid transaction entry
        return None

    if transaction.transaction_type != "transfer":
        entry = transaction.entries[0]
        return TransactionModel(
            id=str(transaction.id),
            account_id=str(entry.account_id),
            transaction_type=transaction.transaction_type,
            amount=entry.amount,
            timestamp=transaction.timestamp.isoformat(),
            category=transaction.category.name                   
        )
    
    if len(transaction.entries) < 2:
        # TODO: log out that there's an invalid transaction entry
        return None
        
    sender, recipient = transaction.entries[0], transaction.entries[1]
    if sender.entry_type == "credit":
        sender, recipient = transaction.entries[1], transaction.entries[0]
    
    return TransactionModel(
        id=str(transaction.id),
        account_id=str(sender.account_id),
        transaction_type=transaction.transaction_type,
        amount=sender.amount,
        timestamp=transaction.timestamp.isoformat(), 
        recipient_id=str(recipient.account_id),
        category=transaction.category.name
    )

def get_categories(user_id: str) -> List[str]:
    statement=(select(TransactionCategories)
        .select_from(Accounts)
        .where(Accounts.user_id.is_(user_id))
        .join(TransactionEntries)
        .join(Transactions)
        .join(TransactionCategories)
        .group_by(TransactionCategories.name)
    )

    categories = db_session.scalars(statement=statement).all()
    return [category.name for category in categories]