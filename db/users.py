from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from models import UserInformation, UserCredential
from db import db_session
from typing import Optional
from .models import User

class UserNotFoundException(Exception):
    id: str
    def __init__(self, id:str):
        super().__init__("user not found")
        self.id = id

def create_user(user: UserCredential) -> str:
    try:
        orm_user = User().from_model(user)
        db_session.add(orm_user)
        db_session.commit()
        return orm_user.id
    except NoResultFound as e:
        db_session.rollback()
        raise UserNotFoundException(id)

def get_user(id:str) -> Optional[UserInformation]:
    try:
        statement = select(User).where(User.id.is_(id))
        user = db_session.scalars(statement=statement).one()
        return user.to_model()
    except NoResultFound as e:
        raise UserNotFoundException(id)
    
def update_user(id: str, user: UserInformation) -> Optional[UserInformation]:
    try:
        statement = select(User).where(User.id.is_(id))
        existing = db_session.scalars(statement=statement).one()
        if existing is None:
            return None
        
        existing.update(user)
        db_session.commit()
        return existing.to_model()
    except NoResultFound as e:
        raise UserNotFoundException(id)
