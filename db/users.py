from sqlalchemy import select
from sqlalchemy.orm import Session
from models import UserInformation, UserCredential
from db import engine, User
from typing import Optional

def create_user(user: UserCredential) -> str:
    orm_user = User().from_model(user)
    with Session(engine) as session:
        session.add(orm_user)
        session.commit()
        return orm_user.id

def get_user(id:str) -> Optional[UserInformation]:
    with Session(engine) as session:
        statement = select(User).where(User.id.is_(id))
        user = session.scalars(statement=statement).one()
        return user.to_model()
    
def update_user(id: str, user: UserInformation) -> Optional[UserInformation]:
    with Session(engine) as session:
        statement = select(User).where(User.id.is_(id))
        existing = session.scalars(statement=statement).one()
        if existing is None:
            return None
        
        existing.update(user)
        session.commit()
        return existing
