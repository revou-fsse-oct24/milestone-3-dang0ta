import os
from app import create_app
from db_inmemory import UserRepository, AccountRepository, TransactionRepository
from auth import AuthRepository

app = create_app(users=UserRepository({}), auth=AuthRepository(), accounts=AccountRepository({}), transactions=TransactionRepository({}))

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(host='0.0.0.0', port=port, debug=debug_mode)