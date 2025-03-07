import os

from dotenv import load_dotenv

load_dotenv()

class AppConfig:
    def __init__(self):
        jwt_secret = os.getenv("JWT_SECRET")
        if not jwt_secret :
            raise RuntimeError("Environment variable 'JWT_SECRET' is required but not set")
        self.JWT_SECRET = jwt_secret