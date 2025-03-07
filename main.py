import os
from app import create_app
from db import UserRepository
from auth import AuthRepository

app = create_app(users=UserRepository({}), auth=AuthRepository())

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)