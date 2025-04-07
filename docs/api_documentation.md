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
    default_account: Optional[Account] # User's default account
    roles: List[str]             # List of user roles (e.g. ["customer"])
    accounts: List[Account]      # List of user's accounts
    created_at: datetime         # User creation timestamp
    updated_at: datetime         # Last update timestamp

class UserCredential(UserInformation):
    password: str               # User's password (hashed)

class CreateUserRequest(BaseModel):
    name: str                    # User's display name
    fullname: str | None         # User's full name (optional)
    email_address: EmailStr      # User's email address
    password: str               # User's password (hashed)
    roles: List[str] = ["customer"] # List of user roles, defaults to ["customer"]
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
    "fullname": "John William Doe",
    "email_address": "john@example.com",
    "password": "password123",
    "roles": ["customer"]
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "id": "user_id",
    "name": "John Doe",
    "fullname": "John William Doe",
    "email_address": "john@example.com",
    "default_account": null,
    "roles": ["customer"],
    "accounts": [],
    "created_at": "2024-03-06T12:00:00Z",
    "updated_at": "2024-03-06T12:00:00Z"
  }
  ```

#### Get Current User
- **GET** `/users/me`
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  {
    "name": "John Doe",
    "fullname": "John William Doe",
    "email_address": "john@example.com",
    "default_account": {
      "id": "account_id",
      "user_id": "user_id",
      "balance": 1000,
      "created_at": "2024-03-06T12:00:00Z",
      "updated_at": "2024-03-06T12:00:00Z"
    },
    "roles": ["customer"],
    "accounts": [
      {
        "id": "account_id",
        "user_id": "user_id",
        "balance": 1000,
        "created_at": "2024-03-06T12:00:00Z",
        "updated_at": "2024-03-06T12:00:00Z"
      }
    ],
    "created_at": "2024-03-06T12:00:00Z",
    "updated_at": "2024-03-06T12:00:00Z"
  }
  ```

#### Update Current User
- **PUT** `/users/me`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "name": "John Doe",
    "fullname": "John William Doe",
    "email_address": "john@example.com"
  }
  ```
- **Response**:
  ```json
  {
    "name": "John Doe",
    "fullname": "John William Doe",
    "email_address": "john@example.com",
    "default_account_id": "account_id",
    "created_at": "2024-03-06T12:00:00Z",
    "updated_at": "2024-03-06T12:00:00Z"
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

### Bill Management

#### Create Bill
- **POST** `/bills`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "biller_name": "Electric Company",
    "due_date": "2024-03-15T00:00:00Z",
    "amount": 100,
    "account_id": "account_id"
  }
  ```
- **Response**:
  ```json
  {
    "bill": {
      "id": "bill_id",
      "biller_name": "Electric Company",
      "due_date": "2024-03-15T00:00:00Z",
      "amount": 100,
      "account_id": "account_id"
    }
  }
  ```

#### Get Bills
- **GET** `/bills`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body** (optional filters):
  ```json
  {
    "account_id": "account_id",
    "biller_name": "Electric%",
    "due_date_from": "2024-03-01T00:00:00Z",
    "due_date_to": "2024-03-31T23:59:59Z",
    "amount_min": 50,
    "amount_max": 200
  }
  ```
- **Response**:
  ```json
  {
    "bills": [
      {
        "id": "bill_id",
        "biller_name": "Electric Company",
        "due_date": "2024-03-15T00:00:00Z",
        "amount": 100,
        "account_id": "account_id"
      }
    ]
  }
  ```

#### Get Bill by ID
- **GET** `/bills/:id`
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  {
    "bill": {
      "id": "bill_id",
      "biller_name": "Electric Company",
      "due_date": "2024-03-15T00:00:00Z",
      "amount": 100,
      "account_id": "account_id"
    }
  }
  ```

#### Update Bill
- **PUT** `/bills/:id`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "biller_name": "Updated Electric Company",
    "due_date": "2024-03-20T00:00:00Z",
    "amount": 150
  }
  ```
- **Response**:
  ```json
  {
    "bill": {
      "id": "bill_id",
      "biller_name": "Updated Electric Company",
      "due_date": "2024-03-20T00:00:00Z",
      "amount": 150,
      "account_id": "account_id"
    }
  }
  ```

#### Delete Bill
- **DELETE** `/bills/:id`
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  {
    "status": "deleted"
  }
  ```

### Budget Management

#### Create Budget
- **POST** `/budgets`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "name": "Monthly Groceries",
    "amount": 500,
    "start_date": "2024-03-01T00:00:00Z",
    "end_date": "2024-03-31T23:59:59Z"
  }
  ```
- **Response**:
  ```json
  {
    "budget": {
      "id": "budget_id",
      "name": "Monthly Groceries",
      "amount": 500,
      "start_date": "2024-03-01T00:00:00Z",
      "end_date": "2024-03-31T23:59:59Z"
    }
  }
  ```

#### Get Budgets
- **GET** `/budgets`
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  {
    "budgets": [
      {
        "id": "budget_id",
        "name": "Monthly Groceries",
        "amount": 500,
        "start_date": "2024-03-01T00:00:00Z",
        "end_date": "2024-03-31T23:59:59Z"
      }
    ]
  }
  ```

#### Get Budget by ID
- **GET** `/budgets/:id`
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  {
    "budget": {
      "id": "budget_id",
      "name": "Monthly Groceries",
      "amount": 500,
      "start_date": "2024-03-01T00:00:00Z",
      "end_date": "2024-03-31T23:59:59Z"
    }
  }
  ```

#### Update Budget
- **PUT** `/budgets/:id`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "name": "Updated Monthly Groceries"
  }
  ```
- **Response**:
  ```json
  {
    "budget": {
      "id": "budget_id",
      "name": "Updated Monthly Groceries",
      "amount": 500,
      "start_date": "2024-03-01T00:00:00Z",
      "end_date": "2024-03-31T23:59:59Z"
    }
  }
  ```

#### Delete Budget
- **DELETE** `/budgets/:id`
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  {
    "result": "deleted"
  }
  ```

### Transaction Categories

#### Get Transaction Categories
- **GET** `/transactions/categories`
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  {
    "categories": ["test"]
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