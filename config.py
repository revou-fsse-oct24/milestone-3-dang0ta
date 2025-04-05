from dotenv import load_dotenv, dotenv_values
import os

# load_dotenv()
# config = dotenv_values(".env")
# db_conn = config["DB_CONN"]
# jwt_secret = config["JWT_SECRET"]
# jwt_algorithm = config["JWT_ALGORITHM"] or "HS256"

db_conn = os.getenv("DB_CONN")
jwt_secret = os.getenv("JWT_SECRET")
jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")