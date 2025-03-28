import bcrypt
from typing import Optional, List, get_args, Literal
from sqlalchemy import ForeignKey, String, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import  Mapped, mapped_column, relationship
from .db import Base
from models import Account as AccountModel, UserCredential, UserInformation, Transaction as TransactionModel

TransactionType = Literal["withdraw", "deposit", "transfer"]
TransactionEntryType = Literal["debit", "credit"]

class Transactions(Base):
    """Represents a transaction in the banking system.
    
    This model holds the core transaction information that isn't related to account ledger changes.
    It has a one-to-many relationship with TransactionEntries, where multiple TransactionEntries
    can refer to a single Transaction.

    Attributes:
        id (int): Primary key of the transaction
        transaction_type (TransactionType): Type of transaction (withdraw/deposit/transfer)
        timestamp (DateTime): When the transaction occurred
        entries (List[TransactionEntries]): List of related transaction entries

    Relationships:
        - Has many TransactionEntries (one-to-many)
    """
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(*get_args(TransactionType), name="transaction_type_enum")
    )
    entries: Mapped[List["TransactionEntries"]] = relationship(
        back_populates="transaction", cascade="all, delete-orphan"
    )
    timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class TransactionEntries(Base):
    """Represents an entry in the account ledger.
    
    This model represents a single entry in the related account's ledger. It has many-to-one
    relationships with both Account and Transactions models.

    Attributes:
        entry_id (int): Primary key of the entry
        amount (int): Transaction amount
        transaction_id (int): Foreign key to Transactions
        account_id (int): Foreign key to Account
        entry_type (TransactionEntryType): Type of entry (debit/credit)

    Relationships:
        - Belongs to one Transaction (many-to-one)
        - Belongs to one Account (many-to-one)

    Methods:
        to_model(): Converts the entry to a TransactionModel
    """
    __tablename__ = "transaction_entries"
    entry_id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[int]

    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"))
    transaction: Mapped["Transactions"] = relationship(back_populates="entries")

    account_id:Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    account:Mapped["Account"] = relationship(back_populates="transaction_entries")

    entry_type: Mapped[TransactionEntryType] = mapped_column(
        Enum(*get_args(TransactionEntryType), name="transaction_entry_type_enum")
    )

    def to_model(self) -> TransactionModel:
        return TransactionModel(
            id=str(self.transaction.id),
            account_id=str(self.account_id),
            transaction_type=self.transaction.transaction_type,
            amount=self.amount,
        )

class Account(Base):
    """Represents a banking account in the system.
    
    This model represents a single banking account with a many-to-one relationship with User,
    where one User can have many accounts. It holds the current balance and has a one-to-many
    relationship with TransactionEntries.

    Attributes:
        id (int): Primary key of the account
        user_id (int): Foreign key to User
        balance (int): Current account balance
        created_at (DateTime): Account creation timestamp
        updated_at (DateTime): Last update timestamp

    Relationships:
        - Belongs to one User (many-to-one)
        - Has many TransactionEntries (one-to-many)

    Methods:
        to_model(): Converts to AccountModel
        update(account: AccountModel): Updates account information
        __repr__(): String representation of the account
    """
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="accounts")

    balance: Mapped[int]
    transaction_entries: Mapped[List["TransactionEntries"]] =  relationship(
        back_populates="account", cascade="all, delete-orphan"
    )

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def to_model(self) -> AccountModel:
        return AccountModel(balance=self.balance)
    
    def update(self, account: AccountModel):
        self.balance = account.balance

    def __repr__(self) -> str:
        return f"Account(id={self.id!r}, user_id={self.user_id!r}, username={self.user.name!r}, balance={self.balance!r})"

class User(Base):
    """Represents a user in the RevoBank system.
    
    This model holds information about the identity of a user and their authentication details.
    It has relationships with Account and Credential models.

    Attributes:
        id (int): Primary key of the user
        name (str): Username (max 30 characters)
        fullname (Optional[str]): User's full name
        email_address (str): User's email address
        created_at (DateTime): User creation timestamp
        updated_at (DateTime): Last update timestamp

    Relationships:
        - Has many Account (one-to-many)
        - Has one Credential (one-to-one)

    Methods:
        from_model(user: UserCredential): Creates user from UserCredential model
        update(user: UserInformation): Updates user information
        add_account(account: AccountModel): Adds a new account to the user
        to_model(): Converts to UserInformation model
        get_accounts(): Returns list of user's accounts
        __repr__(): String representation of the user
    """
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
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

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
    """Stores user password credentials.
    
    This model holds the hashed password of a user and is used for email/password authentication.
    It has a one-to-one relationship with the User model.

    Attributes:
        id (int): Primary key of the credential
        user_id (int): Foreign key to User
        hash (str): Hashed password
        created_at (DateTime): Credential creation timestamp
        updated_at (DateTime): Last update timestamp

    Relationships:
        - Belongs to one User (one-to-one)

    Methods:
        __repr__(): String representation of the credential
    """
    __tablename__ = "user_credentials"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="credential")
    hash: Mapped[str]

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"Credential(id={self.id!r}, user_id={self.user_id!r}, username={self.user.name!r}, hash={self.hash!r})"