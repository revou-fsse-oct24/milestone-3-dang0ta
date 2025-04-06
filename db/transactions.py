from typing import Optional, List, Dict
from db import db_session, Accounts, Transactions, TransactionEntries, Users
from models import Transaction as TransactionModel, TransactionTypes
from .accounts import AccountNotFoundException, AccountsNotFoundException
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload 
from pydantic import BaseModel
from datetime import datetime

class TransactionNotFoundException(Exception):
    def __init__(self, *, transaction_id:str):
        super().__init__("transaction not found")
        self.transaction_id = transaction_id


def withdraw(account_id:str, amount:int, description:str | None = None) -> Optional[TransactionModel]:
    account = db_session.get(Accounts, account_id)
    if account is None:
        raise AccountNotFoundException(account_id=account_id)
    
    account.balance = account.balance - amount
    transaction = Transactions(
        transaction_type="withdraw",
        description=description,
    )

    db_session.add(transaction)
    db_session.flush()

    entry = TransactionEntries(
        transaction_id = transaction.id,
        account_id = account.id,
        entry_type = "debit",
        amount = amount
    )

    db_session.add(entry)
    db_session.commit()
    return TransactionModel(
        id=str(transaction.id),
        account_id=str(account.id),
        transaction_type=transaction.transaction_type,
        amount=amount,
        timestamp=transaction.timestamp.isoformat(),
    )

def deposit(account_id:str, amount:int, description: str | None = None) -> Optional[TransactionModel]:    
    account = db_session.get(Accounts, account_id)
    if account is None:
        raise AccountNotFoundException(account_id=account_id)
    
    account.balance = account.balance + amount
    transaction = Transactions(
        transaction_type="deposit",
        description=description,
    )

    db_session.add(transaction)
    db_session.flush()

    entry = TransactionEntries(
        transaction_id = transaction.id,
        account_id = account.id,
        entry_type = "credit",
        amount=amount
    )
    
    db_session.add(entry)
    db_session.commit()
    return TransactionModel(
        id=str(transaction.id),
        account_id=str(account.id),
        transaction_type=transaction.transaction_type,
        amount=amount,
        timestamp=transaction.timestamp.isoformat(),
    )

def transfer(sender_account_id: str, recipient_account_id: str, amount: int, description:str | None = None) -> Optional[TransactionModel]:
    sender_account = db_session.get(Accounts, sender_account_id)
    if sender_account is None:
        raise AccountNotFoundException(account_id=sender_account_id)
    
    recipient_account = db_session.get(Accounts, recipient_account_id)
    if recipient_account is None:
        raise AccountNotFoundException(account_id=recipient_account_id)

    sender_account.balance = sender_account.balance - amount
    recipient_account.balance = recipient_account.balance + amount

    transaction = Transactions(
        transaction_type="transfer", 
        description=description,
    )

    db_session.add(transaction)
    db_session.flush()

    sender_entry = TransactionEntries(
        transaction_id = transaction.id,
        account_id = sender_account.id,
        entry_type = "debit",
        amount = amount
    )

    recipient_entry = TransactionEntries(
        transaction_id = transaction.id,
        account_id = recipient_account.id,
        entry_type = "credit",
        amount = amount
    )

    db_session.add(sender_entry)
    db_session.add(recipient_entry)
    db_session.commit()
    return TransactionModel(
        id=str(transaction.id),
        account_id=str(sender_account_id),
        transaction_type=transaction.transaction_type,
        amount=sender_entry.amount,
        timestamp=transaction.timestamp.isoformat(),
        recipient_id=str(recipient_entry.account_id)
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
    )
    
    if query.account_id is not None:
        statement = statement.filter(Accounts.id.is_(query.account_id))
    if query.range_from is not None:
        statement = statement.filter(Transactions.timestamp >= query.range_from)
    if query.range_to is not None:
        statement = statement.filter(Transactions.timestamp <= query.range_to)
    if query.transaction_type is not None:
        statement = statement.filter(Transactions.transaction_type.in_(query.transaction_type))
        
    # transactions = db_session.execute(statement=statement.order_by(Transactions.timestamp.desc())).fetchall()
    result = db_session.scalars(statement=statement).all()
    transactions: List[TransactionModel] = []
    for transaction in result:
        if len(transaction.entries) == 0:
            # TODO: maybe we should log this out?
            continue

        if transaction.transaction_type != "transfer":
            entry = transaction.entries[0]
            transactions.append(TransactionModel(
                id=str(transaction.id),
                account_id=str(entry.account_id),
                transaction_type=transaction.transaction_type,
                amount=entry.amount,
                timestamp=transaction.timestamp.isoformat(),                    
            ))
            continue
        
        if len(transaction.entries) < 2:
            # TODO: maybe we should log this out?
            continue
            
        sender, recipient = transaction.entries[0], transaction.entries[1]
        if sender.entry_type == "credit":
            sender, recipient = transaction.entries[1], transaction.entries[0]
        
        transactions.append(TransactionModel(
            id=str(transaction.id),
            account_id=str(sender.account_id),
            transaction_type=transaction.transaction_type,
            amount=sender.amount,
            timestamp=transaction.timestamp.isoformat(), 
            recipient_id=str(recipient.account_id)
        ))

    return transactions
    
def get_transaction(transaction_id:str) -> Optional[TransactionModel]:
    try:

        transaction = db_session.scalars(statement=(
            select(Transactions)
            .filter_by(id=transaction_id)            
        )).one()

        if not transaction:
            raise TransactionNotFoundException(transaction_id=transaction_id)
        
        entries = db_session.scalars(
            select(TransactionEntries).where(TransactionEntries.transaction_id.is_(transaction.id))
        ).all()

        if not entries or len(entries) == 0:
            raise TransactionNotFoundException(transaction_id=transaction_id)

        if len(entries) == 1:
            entry = entries[0]
            return TransactionModel(
                id=str(transaction.id),
                account_id=str(entry.account_id),
                transaction_type=transaction.transaction_type,
                amount=entry.amount,
                timestamp=transaction.timestamp.isoformat(),                
            )

        sender, recipient = entries[0], entries[1]
        if sender.entry_type == "credit":
            sender, recipient = entries[1], entries[0]
        
        return TransactionModel(
            id=str(transaction.id),
            account_id=str(sender.account_id),
            transaction_type=transaction.transaction_type,
            amount=recipient.amount,
            timestamp=transaction.timestamp.isoformat(),    
            recipient_id=str(recipient.account_id)
        )

    except NoResultFound:
        db_session.rollback()
        raise TransactionNotFoundException(transaction_id=transaction_id)