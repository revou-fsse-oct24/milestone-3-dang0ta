import bcrypt
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from db import db_session, Users
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
    
def get_and_compare_hash(email_address:str, password:str) -> str:
    if email_address is None or password is None:
            raise WrongCredentialException(email=email_address)
    try:
        statement = select(Users).where(Users.email_address.is_(email_address))
        user = db_session.scalars(statement=statement).one()
        if user is None:
            raise UserNotFoundException(email=email_address)
        hash = user.credential.hash
        ok = bcrypt.checkpw(password=password.encode(), hashed_password=hash)
        if not ok:
            raise WrongCredentialException(email=email_address)

        return user.id
    except NoResultFound:
        raise UserNotFoundException(email=email_address)

