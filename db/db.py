import bcrypt
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from flask import current_app as app
from models import UserCredential, UserInformation


class Base(DeclarativeBase):
    pass

class User(Base):
    "This is ORM-related User model, intended for retrieving and writing data to DB"
    "other than the following properties, the properties of this class has to be the exact same as the same class defined in model"

    __tablename__ = "user_accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]

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
        return self
    
    def update(self, user: UserInformation):
        self.name = user.name
        self.fullname = user.fullname
        self.email_address = user.email_address
    
    def to_model(self) -> UserInformation:
        return UserInformation(name=self.name, fullname=self.fullname, email_address=self.email_address)

class Credential(Base):
    __tablename__ = "user_credentials"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_accounts.id"))
    user: Mapped["User"] = relationship(back_populates="credential")
    
    hash: Mapped[str]
    
engine = create_engine("sqlite://", echo=True)
Base.metadata.create_all(engine)