from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from models import UserInformation, UserCredential
from db import engine, User
from typing import Optional

class UserNotFoundException(Exception):
    id: str
    def __init__(self, id:str):
        super().__init__("user not found")
        self.id = id

def create_user(user: UserCredential) -> str:
    try:
        orm_user = User().from_model(user)
        with Session(engine) as session:
            session.add(orm_user)
            session.commit()
            return orm_user.id
    except NoResultFound as e:
        raise UserNotFoundException(id)

def get_user(id:str) -> Optional[UserInformation]:
    try:
        with Session(engine) as session:
            statement = select(User).where(User.id.is_(id))
            user = session.scalars(statement=statement).one()
            return user.to_model()
    except NoResultFound as e:
        raise UserNotFoundException(id)
    
def update_user(id: str, user: UserInformation) -> Optional[UserInformation]:
    try:
        with Session(engine) as session:
            statement = select(User).where(User.id.is_(id))
            existing = session.scalars(statement=statement).one()
            if existing is None:
                return None
            
            existing.update(user)
            session.commit()
            return existing.to_model()
    except NoResultFound as e:
        raise UserNotFoundException(id)
