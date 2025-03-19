import bcrypt
from typing import Optional, List
from sqlalchemy import select, ForeignKey, String
from sqlalchemy.orm import  Mapped, mapped_column, relationship
from .db import Base
from models import Account as AccountModel, UserCredential, UserInformation

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="accounts")

    balance: Mapped[int]

    def to_model(self) -> AccountModel:
        return AccountModel(balance=self.balance)
    
    def update(self, account: AccountModel):
        self.balance = account.balance

    def __repr__(self) -> str:
        return f"Account(id={self.id!r}, user_id={self.user_id!r}, username={self.user.name!r}, balance={self.balance!r})"

class User(Base):
    "This is ORM-related User model, intended for retrieving and writing data to DB"
    "other than the following properties, the properties of this class has to be the exact same as the same class defined in model"

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]

    accounts: Mapped[List["Account"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    credential: Mapped["Credential"] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    email_address: Mapped[str]

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"
    
    def from_model(self, user: UserCredential):
        self.credential = Credential(
            user_id=self.id,
            user=self,
            hash=bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
        )

        self.update(user.info())
        self.accounts = []
        return self
    
    def update(self, user: UserInformation):
        self.name = user.name
        self.fullname = user.fullname
        self.email_address = user.email_address

    def add_account(self, account: AccountModel) -> Account:
        orm_account = Account(
            user_id=self.id,
            user=self,
            balance= account.balance
        )
        self.accounts.append(orm_account)
        return orm_account
    
    def to_model(self) -> UserInformation:
        return UserInformation(name=self.name, fullname=self.fullname, email_address=self.email_address)
    
    def get_accounts(self) -> List[AccountModel]:
        accounts = []
        for acc in self.accounts:
            accounts.append(acc.to_model())
        return accounts
    
class Credential(Base):
    __tablename__ = "user_credentials"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="credential")
    hash: Mapped[str]

    def __repr__(self) -> str:
        return f"Credential(id={self.id!r}, user_id={self.user_id!r}, username={self.user.name!r}, hash={self.hash!r})"