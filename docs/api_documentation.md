# RevoBank API Documentation

## Table of Contents
1. [Application Design](#application-design)
2. [Database Models](#database-models)
3. [API Endpoints](#api-endpoints)
4. [Authentication](#authentication)
5. [Error Handling](#error-handling)
6. [Libraries Used](#libraries-used)

## Application Design

The RevoBank API is built using a modular architecture with the following components:

### Core Components
- **Flask Application**: Main application server
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation and serialization
- **JWT**: Authentication and authorization

### Directory Structure
```
.
├── app.py              # Application entry point
├── config.py           # Configuration management
├── models.py           # Pydantic models for data validation
├── routes/             # API route handlers
│   ├── auth.py         # Authentication endpoints
│   ├── user.py         # User management endpoints
│   ├── accounts.py     # Account management endpoints
│   └── transactions.py # Transaction endpoints
├── db/                 # Database models and operations
├── auth_jwt/           # JWT authentication implementation
└── tests/              # Test suite
```

## Database Models

### User Models
```python
class UserInformation(BaseModel):
    name: str                    # User's display name
    fullname: str | None         # User's full name (optional)
    email_address: EmailStr      # User's email address
    default_account_id: str | None # ID of user's default account

class UserCredential(UserInformation):
    password: str               # User's password (hashed)
```

### Account Models
```python
class Account(BaseModel):
    id: str                     # Unique account identifier
    user_id: str                # ID of account owner
    balance: int                # Current account balance
    created_at: datetime        # Account creation timestamp
    updated_at: datetime        # Last update timestamp
```

### Transaction Models
```python
class TransactionTypes(str, Enum):
    withdraw = "withdraw"
    deposit = "deposit"
    transfer = "transfer"

class Transaction(BaseModel):
    id: str                     # Unique transaction identifier
    account_id: str             # Source account ID
    transaction_type: TransactionTypes # Type of transaction
    amount: int                 # Transaction amount
    timestamp: datetime         # Transaction timestamp
    recipient_id: str | None    # Recipient account ID (for transfers)
```

## API Endpoints

### Authentication

#### Login
- **POST** `/auth/login`
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "jwt_token",
    "refresh_token": "refresh_token"
  }
  ```

#### Refresh Token
- **POST** `/auth/refresh`
- **Request Body**:
  ```json
  {
    "refresh_token": "refresh_token"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "new_jwt_token"
  }
  ```

#### Logout
- **GET** `/auth/logout`
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  {
    "message": "Logged out successfully"
  }
  ```

### User Management

#### Create User
- **POST** `/users`
- **Request Body**:
  ```json
  {
    "name": "John Doe",
    "email_address": "john@example.com",
    "password": "password123"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "id": "user_id"
  }
  ```

#### Get Current User
- **GET** `/users/me`
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  {
    "name": "John Doe",
    "email_address": "john@example.com",
    "default_account_id": "account_id"
  }
  ```

#### Update Current User
- **PUT** `/users/me`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "name": "John Doe",
    "email_address": "john@example.com"
  }
  ```
- **Response**:
  ```json
  {
    "name": "John Doe",
    "email_address": "john@example.com",
    "default_account_id": "account_id"
  }
  ```

### Account Management

#### Get All Accounts
- **GET** `/accounts`
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  {
    "accounts": [
      {
        "id": "account_id",
        "balance": 1000,
        "created_at": "2024-03-06T12:00:00Z",
        "updated_at": "2024-03-06T12:00:00Z"
      }
    ]
  }
  ```

#### Get Account by ID
- **GET** `/accounts/:id`
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  {
    "id": "account_id",
    "balance": 1000,
    "created_at": "2024-03-06T12:00:00Z",
    "updated_at": "2024-03-06T12:00:00Z"
  }
  ```

#### Create Account
- **POST** `/accounts`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "balance": 1000
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "account": {
      "id": "account_id",
      "balance": 1000,
      "created_at": "2024-03-06T12:00:00Z",
      "updated_at": "2024-03-06T12:00:00Z"
    }
  }
  ```

#### Update Account
- **PUT** `/accounts/:id`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "balance": 2000
  }
  ```
- **Response**:
  ```json
  {
    "balance": 2000
  }
  ```

#### Delete Account
- **DELETE** `/accounts/:id`
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  {
    "result": "deleted"
  }
  ```

### Transaction Management

#### Get All Transactions
- **GET** `/transactions`
- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**:
  - `transaction_type`: Filter by type (withdraw/deposit/transfer)
  - `account_id`: Filter by account
  - `range_from`: Filter by start date
  - `range_to`: Filter by end date
- **Response**:
  ```json
  {
    "transactions": [
      {
        "id": "transaction_id",
        "account_id": "account_id",
        "transaction_type": "deposit",
        "amount": 1000,
        "timestamp": "2024-03-06T12:00:00Z",
        "recipient_id": null
      }
    ]
  }
  ```

#### Get Transaction by ID
- **GET** `/transactions/:id`
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  {
    "transaction": {
      "id": "transaction_id",
      "account_id": "account_id",
      "transaction_type": "deposit",
      "amount": 1000,
      "timestamp": "2024-03-06T12:00:00Z",
      "recipient_id": null
    }
  }
  ```

#### Create Withdrawal
- **POST** `/transactions/withdraw`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "account_id": "account_id",
    "amount": 1000
  }
  ```
- **Response**:
  ```json
  {
    "transaction": {
      "id": "transaction_id",
      "account_id": "account_id",
      "transaction_type": "withdraw",
      "amount": 1000,
      "timestamp": "2024-03-06T12:00:00Z",
      "recipient_id": null
    }
  }
  ```

#### Create Deposit
- **POST** `/transactions/deposit`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "account_id": "account_id",
    "amount": 1000
  }
  ```
- **Response**:
  ```json
  {
    "transaction": {
      "id": "transaction_id",
      "account_id": "account_id",
      "transaction_type": "deposit",
      "amount": 1000,
      "timestamp": "2024-03-06T12:00:00Z",
      "recipient_id": null
    }
  }
  ```

#### Create Transfer
- **POST** `/transactions/transfer`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "account_id": "account_id",
    "recipient_account_id": "recipient_account_id",
    "amount": 1000
  }
  ```
- **Response**:
  ```json
  {
    "transaction": {
      "id": "transaction_id",
      "account_id": "account_id",
      "transaction_type": "transfer",
      "amount": 1000,
      "timestamp": "2024-03-06T12:00:00Z",
      "recipient_id": "recipient_account_id"
    }
  }
  ```

## Error Handling

The API uses standard HTTP status codes and returns error messages in JSON format:

```json
{
  "error": "Error message description"
}
```

Common error codes:
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

## Libraries Used

- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation and serialization
- **JWT**: Authentication
- **pytest**: Testing framework
- **uv**: Python package manager
- **Docker**: Containerization 