from typing import List, Optional
from models import Account as AccountModel, CreateAccountRequest, UpdateAccountRequest
from sqlalchemy import select, delete
from sqlalchemy.exc import NoResultFound
from db import db_session, Users, Accounts

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
        statement=select(Users).where(Users.id.is_(user_id))
        user = db_session().scalars(statement=statement).one()
        return user.get_accounts()
    except NoResultFound:
        raise AccountsNotFoundException(user_id=user_id)
    
def get_account(user_id:str, account_id:str) -> Optional[AccountModel]:
    try:
        statement = (
            select(Accounts)
            .filter(Accounts.id.is_(account_id))
            .filter(Accounts.user_id.is_(user_id))
        )

        account = db_session.scalars(statement=statement).one()
        return account.to_model()
    except NoResultFound:
        raise AccountNotFoundException(account_id=account_id)

# CONCERN: Do we really need an update endpoint for accounts? Accounts should be modifiable 
# through actions like transfer, withdraw, or deposit, right? since the actions will also 
# produce transaction traces that we can use to verify the account integrity. Anyway, let's 
# do this as an exercise.
def update_account(user_id:str, request: UpdateAccountRequest) -> Optional[AccountModel]:
    try:
        if request.account_id:
            account = db_session.query(Accounts).filter_by(id=request.account_id).first()
        else:
            user = db_session.query(Users).filter_by(id=user_id).first()
            if not user or not user.default_account_id:
                raise AccountsNotFoundException(user_id=user_id)
            
            account = db_session.query(Accounts).filter_by(id=user.default_account_id).first()

        if not account:
            raise AccountsNotFoundException(user_id=user_id)
            
        account.balance = request.balance
        db_session.commit()
        return account.to_model()
    except NoResultFound as e:
        db_session.rollback()
        raise AccountsNotFoundException(user_id=user_id)
    
def create_account(user_id:str, request: CreateAccountRequest) -> AccountModel:
    try:
        account = Accounts(balance=request.balance, user_id=int(user_id))
        db_session.add(account)
        db_session.commit()
        return account.to_model()
    except NoResultFound as e:
        db_session.rollback()
        raise AccountNotFoundException(account_id="")
    
def delete_account(user_id:str, account_id:str):
    try:
        statement = delete(Accounts).where(Accounts.id.is_(account_id)).returning(Accounts.id)
        result = db_session.execute(statement=statement).one()
        db_session.commit()
        db_session.flush()
        return result[0]
    except NoResultFound as e:
        db_session.rollback()
        raise AccountNotFoundException(account_id=account_id)
    

