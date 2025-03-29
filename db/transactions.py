from typing import Optional, List, Dict
from db import db_session, Accounts, Transactions, TransactionEntries
from models import Transaction as TransactionModel
from .accounts import AccountNotFoundException, AccountsNotFoundException
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

class TransactionNotFoundException(Exception):
    def __init__(self, *, transaction_id:str):
        super().__init__("transaction not found")
        self.transaction_id = transaction_id


def withdraw(account_id:str, amount:int) -> Optional[TransactionModel]:
    try:
        statement = (
            select(Accounts)
            .where(Accounts.id.is_(account_id))
        )

        account = db_session.scalars(statement=statement).one()
        
        account.balance = account.balance - amount
        transaction = Transactions(
            transaction_type="withdraw"
        )

        entry = TransactionEntries(
            transaction_id = transaction.id,
            transaction = transaction,
            account_id = account_id,
            account = account,
            entry_type = "debit",
            amount = amount
        )

        db_session.add(transaction)
        db_session.add(entry)
        db_session.commit()
        return entry.to_model()
    except NoResultFound:
        db_session.rollback()
        raise AccountNotFoundException(account_id=account_id)
    except Exception as e:
        db_session.rollback()
        raise e

def deposit(account_id:str, amount:int) -> Optional[TransactionModel]:
    try:
        statement = (
            select(Accounts)
            .where(Accounts.id.is_(account_id))
        )

        account = db_session.scalars(statement=statement).one()
        
        account.balance = account.balance + amount
        transaction = Transactions(
            transaction_type="deposit"
        )

        entry = TransactionEntries(
            transaction_id = transaction.id,
            transaction = transaction,
            account_id = account.id,
            account = account,
            entry_type = "credit",
            amount=amount
        )

        db_session.add(transaction)
        db_session.add(entry)
        db_session.commit()
        return entry.to_model()
    except NoResultFound:
        db_session.rollback()
        raise AccountNotFoundException(account_id=account_id)
    except Exception as e:
        db_session.rollback()
        raise e

def transfer(sender_account_id: str, recipient_account_id: str, amount: int) -> Optional[TransactionModel]:
    try:
        sender_account = db_session.scalars(statement=(
            select(Accounts)
            .where(Accounts.id.is_(sender_account_id))
        )).one()

        sender_account.balance = sender_account.balance - amount

        recipient_account = db_session.scalars(statement=(
            select(Accounts)
            .where(Accounts.id.is_(recipient_account_id))
        )).one()

        recipient_account.balance = recipient_account.balance + amount

        transaction = Transactions(
            transaction_type="transfer"
        )

        sender_entry = TransactionEntries(
            transaction_id = transaction.id,
            transaction = transaction,
            account_id = sender_account_id,
            account = sender_account,
            entry_type = "debit",
            amount = amount
        )

        recipient_entry = TransactionEntries(
            transaction_id = transaction.id,
            transaction = transaction,
            account_id = recipient_account_id,
            account = recipient_account,
            entry_type = "credit",
            amount = amount
        )

        db_session.add(transaction)
        db_session.add(sender_entry)
        db_session.add(recipient_entry)
        db_session.commit()
        return sender_entry.to_model()
    except NoResultFound as e:
        db_session.rollback()
        raise AccountNotFoundException(account_id=sender_account_id)
    except Exception as e:
        db_session.rollback()
        raise e
    
def get_transactions(account_id: str) -> List[TransactionModel]:
    try:
        accounts=db_session.scalars(statement=(
            select(Accounts)
            .where(Accounts.id.is_(account_id))
        ))

        transactions: List[Dict] = []
        for account in accounts:
            for transaction in account.transaction_entries:
                transactions.append(transaction.to_model().model_dump())

        return transactions
    except NoResultFound:
        db_session.rollback()
        raise AccountNotFoundException(account_id=account_id)
    except Exception as e:
        db_session.rollback()
        raise e
    
def get_transaction(transaction_id:str) -> Optional[TransactionModel]:
    try:

        entry = db_session.scalars(statement=(
            select(TransactionEntries)
            .where(TransactionEntries.transaction_id.is_(transaction_id))
        )).one()
        
        

        return entry.to_model()
    except NoResultFound:
        db_session.rollback()
        raise TransactionNotFoundException(transaction_id=transaction_id)