import bcrypt
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from models import UserInformation, UserCredential, CreateUserRequest
from db import db_session, Users, Accounts, Credentials
from typing import Optional

class UserNotFoundException(Exception):
    id: str
    def __init__(self, id:str):
        super().__init__("user not found")
        self.id = id

def create_user(request: CreateUserRequest) -> str:
    try:
        user = Users(
            name=request.name,
            fullname=request.fullname,     
            email_address= request.email_address,       
        )
        
        db_session.add(user)
        db_session.flush()
        account = Accounts(
            user_id=user.id,
            balance=0,
        )

        credential = Credentials(
            user_id=user.id,
            hash=bcrypt.hashpw(request.password.encode(), bcrypt.gensalt())
        )

        db_session.add_all([account, credential])
        db_session.flush()

        user.default_account_id = account.id

        db_session.commit()
        return user.id
    except Exception as e:
        db_session.rollback()
        raise e

def get_user(id:str) -> Optional[UserInformation]:
    try:
        statement = select(Users).where(Users.id.is_(id))
        user = db_session.scalars(statement=statement).one()
        return user.to_model()
    except NoResultFound:
        raise UserNotFoundException(id)
    
def update_user(id: str, user: UserInformation) -> Optional[UserInformation]:
    try:
        statement = select(Users).where(Users.id.is_(id))
        existing = db_session.scalars(statement=statement).one()
        existing.update(user)
        db_session.commit()
        return existing.to_model()
    except NoResultFound as e:
        raise UserNotFoundException(id)
