# Database Models Documentation

This document provides detailed information about the database models used in the RevoBank system. The system uses SQLAlchemy ORM for database operations.

## Models Overview

The system consists of the following main models:
- `Transactions` - Core transaction information
- `TransactionEntries` - Individual ledger entries for transactions
- `Account` - Banking account information
- `User` - User information and authentication
- `Credential` - User password credentials

## Transaction Models

### Transactions
The `Transactions` model represents the core transaction information in the banking system.

**Table Name:** `transactions`

**Fields:**
- `id` (int): Primary key
- `transaction_type` (enum): Type of transaction
  - Possible values: "withdraw", "deposit", "transfer"
- `timestamp` (DateTime): When the transaction occurred
- `entries` (List[TransactionEntries]): One-to-many relationship with transaction entries

**Relationships:**
- Has many `TransactionEntries` (one-to-many)

### TransactionEntries
The `TransactionEntries` model represents individual entries in the account ledger.

**Table Name:** `transaction_entries`

**Fields:**
- `entry_id` (int): Primary key
- `amount` (int): Transaction amount
- `transaction_id` (int): Foreign key to Transactions
- `account_id` (int): Foreign key to Account
- `entry_type` (enum): Type of entry
  - Possible values: "debit", "credit"

**Relationships:**
- Belongs to one `Transaction` (many-to-one)
- Belongs to one `Account` (many-to-one)

**Methods:**
- `to_model()`: Converts the entry to a TransactionModel

## Account Model

The `Account` model represents a banking account in the system.

**Table Name:** `accounts`

**Fields:**
- `id` (int): Primary key
- `user_id` (int): Foreign key to User
- `balance` (int): Current account balance
- `created_at` (DateTime): Account creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Relationships:**
- Belongs to one `User` (many-to-one)
- Has many `TransactionEntries` (one-to-many)

**Methods:**
- `to_model()`: Converts to AccountModel
- `update(account: AccountModel)`: Updates account information
- `__repr__()`: String representation of the account

## User Models

### User
The `User` model represents a user in the RevoBank system.

**Table Name:** `users`

**Fields:**
- `id` (int): Primary key
- `name` (str): Username (max 30 characters)
- `fullname` (Optional[str]): User's full name
- `email_address` (str): User's email address
- `created_at` (DateTime): User creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Relationships:**
- Has many `Account` (one-to-many)
- Has one `Credential` (one-to-one)

**Methods:**
- `from_model(user: UserCredential)`: Creates user from UserCredential model
- `update(user: UserInformation)`: Updates user information
- `add_account(account: AccountModel)`: Adds a new account to the user
- `to_model()`: Converts to UserInformation model
- `get_accounts()`: Returns list of user's accounts
- `__repr__()`: String representation of the user

### Credential
The `Credential` model stores user password information.

**Table Name:** `user_credentials`

**Fields:**
- `id` (int): Primary key
- `user_id` (int): Foreign key to User
- `hash` (str): Hashed password
- `created_at` (DateTime): Credential creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Relationships:**
- Belongs to one `User` (one-to-one)

**Methods:**
- `__repr__()`: String representation of the credential

## Type Definitions

### TransactionType
```python
TransactionType = Literal["withdraw", "deposit", "transfer"]
```

### TransactionEntryType
```python
TransactionEntryType = Literal["debit", "credit"]
```

## Notes
- All timestamps are stored with timezone information
- Passwords are hashed using bcrypt before storage
- The system uses SQLAlchemy's relationship system for managing model associations
- Cascade delete is implemented for related records 