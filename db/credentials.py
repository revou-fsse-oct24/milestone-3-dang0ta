from sqlalchemy import select
from sqlalchemy.orm import Session
from db import engine, User

def get_hash(email_address:str) -> str:
    with Session(engine) as session:
        statement = select(User).where(User.email_address.is_(email_address))
        user = session.scalars(statement=statement).one()
        return user.credential.hash