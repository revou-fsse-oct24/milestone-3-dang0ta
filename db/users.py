import bcrypt
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload
from models import UserInformation, CreateUserRequest, Account as AccountModel
from db import db_session, Users, Accounts, Credentials
from typing import Optional

class UserNotFoundException(Exception):
    id: str
    def __init__(self, id:str):
        super().__init__("user not found")
        self.id = id

def create_user(request: CreateUserRequest) -> str:
    user = Users(
        username=request.name,
        fullname=request.fullname,     
        email=request.email_address,     
        roles=",".join(request.roles)
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

def get_user(id:str) -> Optional[UserInformation]:
    try:
        statement = select(Users).where(Users.id.is_(id)).options(joinedload(Users.accounts)).options(joinedload(Users.default_account))
        user = db_session.scalars(statement=statement).unique().one()
        return UserInformation(
            name=user.username,
            fullname=user.fullname,
            email_address=user.email,
            default_account=AccountModel(
                id=str(user.default_account.id),
                user_id=str(user.id),
                balance=user.default_account.balance,
                created_at=user.default_account.created_at.isoformat(),
                updated_at=user.default_account.updated_at.isoformat(),
            ),
            roles=user.roles.split(","),
            accounts=[AccountModel(
                id=str(account.id),
                user_id=str(user.id),
                balance=account.balance,
                created_at=account.created_at.isoformat(),
                updated_at=account.updated_at.isoformat(),
            ) for account in user.accounts],
        )
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
