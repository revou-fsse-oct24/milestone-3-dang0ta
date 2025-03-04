import os
from src.app import create_app
from src.db import UserRepository
app = create_app(users=UserRepository({}))

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)