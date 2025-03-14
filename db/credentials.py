import bcrypt
from sqlalchemy import select
from sqlalchemy.orm import Session
from db import engine, User

class UserNotFoundException(Exception):
    # keep the email for logging
    email: str
    def __init__(self, email: str):
        super().__init__("the given user credential is not found")
        self.email = email

class WrongCredentialException(Exception):
    # keep the email for logging
    email: str
    def __init__(self, email):
        super().__init__("incorrect email/password")
        self.email = email


def get_hash(email_address:str) -> str:
    with Session(engine) as session:
        statement = select(User).where(User.email_address.is_(email_address))
        user = session.scalars(statement=statement).one()
        return user.credential.hash
    
def get_and_compare_hash(email_address:str, password:str) -> str:
    if email_address is None or password is None:
            raise WrongCredentialException(email=email_address)
    with Session(engine) as session:
        statement = select(User).where(User.email_address.is_(email_address))
        user = session.scalars(statement=statement).one()
        if user is None:
            raise UserNotFoundException(email=email_address)
        hash = user.credential.hash
        ok = bcrypt.checkpw(password=password.encode(), hashed_password=hash)
        if not ok:
            WrongCredentialException(email=email_address)

        return user.id

