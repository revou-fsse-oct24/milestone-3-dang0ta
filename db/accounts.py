from typing import List, Optional
from models import Account as AccountModel
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from db import Base, db_session
from .models import User, Account


class AccountsNotFoundException(Exception):
    def __init__(self, user_id:str):
        super().__init__("account not found")
        self.user_id = user_id

class AccountNotFoundException(Exception):
    def __init__(self, account_id: str):
        super().__init__("account not found")
        self.account_id = account_id

def get_accounts(user_id:str) -> List[AccountModel]:
    try:
        statement=select(User).where(User.id.is_(user_id))
        user = db_session.scalars(statement=statement).one()
        if user is None:
            return []
        
        return user.get_accounts()
    except NoResultFound:
        raise AccountsNotFoundException(user_id=user_id)
    
def get_account(user_id:str, account_id:str) -> Optional[AccountModel]:
    try:
        statement = (
            select(Account)
            .join(User)
            .where(Account.id.is_(account_id))
            .where(User.id.is_(user_id))
        )

        account = db_session.scalars(statement=statement).one()
        if account is None:
            return None
        
        return account.to_model()
    except NoResultFound:
        raise AccountNotFoundException(account_id=account_id)
    
def update_account(user_id:str, account_id:str, account: AccountModel) -> Optional[AccountModel]:
    try:
        statement = (
            select(Account)
            .join(User)
            .where(Account.id.is_(account_id))
            .where(User.id.is_(user_id))
        )

        existing = db_session.scalars(statement=statement).one()
        if existing is None:
            return None
        
        existing.update(account)
        db_session.commit()
        return existing.to_model()
    except NoResultFound as e:
        db_session.rollback()
        raise AccountNotFoundException(account_id=account_id)
    except Exception as e:
        db_session.rollback()
        raise e
    
def create_account(user_id:str, account: AccountModel) -> Optional[str]:
    try:
        statement = select(User).where(User.id.is_(user_id))
        user = db_session.scalars(statement=statement).one()
        if user is None:
            return None
        
        added = user.add_account(account)
        db_session.commit()
        return added.id
    except NoResultFound as e:
        db_session.rollback()
        raise AccountNotFoundException(account_id="")
    except Exception as e:
        db_session.rollback()
        raise e
    
        
def delete_account(user_id:str, account_id:str):
    try:
        user = db_session.get(User, user_id)
        account = db_session.get(Account, account_id)
        user.accounts.remove(account)
        db_session.commit()
        db_session.flush()
    except NoResultFound as e:
        db_session.rollback()
        raise AccountNotFoundException(account_id=account_id)
    except Exception as e:
        db_session.rollback()
        raise e