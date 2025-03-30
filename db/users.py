from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from models import UserInformation, UserCredential
from db import db_session, Users
from typing import Optional

class UserNotFoundException(Exception):
    id: str
    def __init__(self, id:str):
        super().__init__("user not found")
        self.id = id

def create_user(user: UserCredential) -> str:
    try:
        orm_user = Users().from_model(user)
        db_session.add(orm_user)
        db_session.commit()
        return orm_user.id
    except NoResultFound as e:
        db_session.rollback()
        raise UserNotFoundException(id)
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
        if existing is None:
            return None
        
        existing.update(user)
        db_session.commit()
        return existing.to_model()
    except NoResultFound as e:
        raise UserNotFoundException(id)
