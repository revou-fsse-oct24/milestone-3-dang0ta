# RevoBank API

A RESTful API for the RevoBank application, implemented with Python and Flask. This API provides banking functionalities including user management, account management, and transactions.

## Activity Diagram
This [documentation](docs/activity_diagram.md) covers all the activity diagrams.

## Features (WIP)

- User authentication and authorization with JWT
- Account management (create, read, update, delete)
- Transaction processing (deposits, withdrawals, transfers)
- In-memory database (can be easily replaced with any SQL database)

## API Endpoints (WIP)

### User Management
- `POST /users` - Create a new user account
- `POST /users/login` - User login
- `GET /users/me` - Retrieve current user profile
- `PUT /users/me` - Update current user profile

### Account Management
- `GET /accounts` - Retrieve all accounts for current user
- `GET /accounts/:id` - Retrieve specific account by ID
- `POST /accounts` - Create a new account
- `PUT /accounts/:id` - Update an account
- `DELETE /accounts/:id` - Delete an account

### Transaction Management
- `GET /transactions` - Retrieve all transactions for user's accounts
- `GET /transactions/:id` - Retrieve a specific transaction
- `POST /transactions` - Create a new transaction (deposit, withdrawal, transfer)

## Installation

1. Clone the repository
2. Syncronize the dependencies
   ```bash
   uv sync
   ```
3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in the required values
5. Start the server:
   ```bash
   uv run ./main.py
   ```

## Usage Examples

### Create a user

```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
  }'
```


## Testing and Code Coverage

To run tests (with code coverage, current coverage is around 93%):
```bash
uv run pytest --cov=.
```

latest coverage: taken at Wednesday, March 12, 2025:
![coverage](docs/latest_coverage.png)

## Live API
The server is up and ready for public access at [this link](disciplinary-sisile-dang0ta-1963dd4c.koyeb.app).