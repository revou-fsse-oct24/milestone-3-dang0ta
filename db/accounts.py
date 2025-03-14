from typing import List, Optional
from models import Account as AccountModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from db import engine, User, Account

class AccountsNotFoundException(Exception):
    def __init__(self, user_id:str):
        super().__init__("account not found")
        self.user_id = user_id

class AccountNotFoundException(Exception):
    def __init__(self, user_id:str, account_id: str):
        super().__init__("account not found")
        self.user_id = user_id
        self.account_id = account_id

def get_accounts(user_id:str) -> List[AccountModel]:
    try:
        with Session(engine) as session:
            statement=select(User).where(User.id.is_(user_id))
            user = session.scalars(statement=statement).one()
            if user is None:
                return []
            
            return user.get_accounts()
    except NoResultFound:
        raise AccountsNotFoundException(user_id=user_id)
    
def get_account(user_id:str, account_id:str) -> Optional[AccountModel]:
    try:
        with Session(engine) as session:
            statement = (
                select(Account)
                .join(User)
                .where(Account.id.is_(account_id))
                .where(User.id.is_(user_id))
            )

            account = session.scalars(statement=statement).one()
            if account is None:
                return None
            
            return account.to_model()
    except NoResultFound:
        raise AccountNotFoundException(user_id=user_id, account_id=account_id)
    
def update_account(user_id:str, account_id:str, account: AccountModel) -> Optional[AccountModel]:
    with Session(engine) as session:
        statement = (
            select(Account)
            .join(User)
            .where(Account.id.is_(account_id))
            .where(User.id.is_(user_id))
        )

        existing = session.scalars(statement=statement).one()
        if existing is None:
            return None
        
        existing.update(account)
        session.commit()
        return existing.to_model()
    
def create_account(user_id:str, account: AccountModel) -> Optional[str]:
    with Session(engine) as session:
        statement = select(User).where(User.id.is_(user_id))
        user = session.scalars(statement=statement).one()
        if user is None:
            return None
        
        added = user.add_account(account)
        session.commit()
        return added.id
        
def delete_account(user_id:str, account_id:str):
    with Session(engine) as session:
        user = session.get(User, user_id)
        account = session.get(Account, account_id)
        user.accounts.remove(account)
        session.commit()
        session.flush()