from typing import Optional, List
from db import db_session
from models import Transaction as TransactionModel
from .accounts import AccountNotFoundException, AccountsNotFoundException
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from .models import Account, Transaction, User

class TransactionNotFoundException(Exception):
    def __init__(self, *, transaction_id:str):
        self.transaction_id = transaction_id
        super.__init__("transaction not found")

def withdraw(account_id:str, amount:int) -> Optional[TransactionModel]:
    try:
        statement = (
            select(Account)
            .where(Account.id.is_(account_id))
        )

        account = db_session.scalars(statement=statement).one()
        account.balance = account.balance - amount
        transaction = Transaction(
            amount=amount,
            account_id=account_id,
            account=account,
            transaction_type="withdraw"
        )

        db_session.add(transaction)
        db_session.commit()
        return transaction.to_model()
    except NoResultFound:
        db_session.rollback()
        raise AccountNotFoundException(account_id=account_id)
    except Exception:
        db_session.rollback()

def deposit(account_id:str, amount:int) -> Optional[TransactionModel]:
    try:
        statement = (
            select(Account)
            .where(Account.id.is_(account_id))
        )

        account = db_session.scalars(statement=statement).one()
        account.balance = account.balance - amount
        transaction = Transaction(
            amount=amount,
            account_id=account_id,
            account=account,
            transaction_type="withdraw"
        )

        db_session.add(transaction)
        db_session.commit()
        return transaction.to_model()
    except NoResultFound:
        db_session.rollback()
        raise AccountNotFoundException(account_id=account_id)
    except Exception as e:
        db_session.rollback()
        raise e

def transfer(account_id: str, recipient_account_id: str, amount: int) -> Optional[TransactionModel]:
    try:

        account = db_session.scalars(statement=(
            select(Account)
            .where(Account.id.is_(account_id))
        )).one()

        account.balance = account.balance - amount

        recipient_account = db_session.scalars(statement=(
            select(Account)
            .where(Account.id.is_(recipient_account_id))
        )).one()

        recipient_account.balance = recipient_account.balance + amount
        
        transaction = Transaction(
            amount=amount,
            account_id=account_id,
            recipient_account_id=recipient_account_id,
            recipient_account=recipient_account,
            transaction_type="transfer"
        )

        db_session.add(transaction)
        db_session.commit()
        return transaction.to_model()
    except NoResultFound:
        db_session.rollback()
        raise AccountNotFoundException(account_id=account_id)
    except Exception as e:
        db_session.rollback()
        raise e
    
def get_transactions(user_id: str) -> List[TransactionModel]:
    try:
        accounts=db_session.scalars(statement=(
            select(Account)
            .join(User)
            .where(User.id.is_(user_id))
        ))

        transactions: List[TransactionModel] = []
        for account in accounts:
            for transaction in account.transactions:
                transactions.append(transaction.to_model())

        return transactions
    except NoResultFound:
        db_session.rollback()
        raise AccountsNotFoundException(user_id=user_id)
    except Exception as e:
        db_session.rollback()
        raise e
    
def get_transaction(transaction_id:str) -> Optional[TransactionModel]:
    try:
        transaction=db_session.scalars(statement=(
            select(Transaction)
            .where(Transaction.id.is_(transaction_id))
        )).one()

        return transaction.to_model()
    except NoResultFound:
        db_session.rollback()
        raise TransactionNotFoundException(transaction_id==transaction_id)