from dotenv import load_dotenv, dotenv_values

load_dotenv()
config = dotenv_values(".env")
db_conn = config["DB_CONN"]
jwt_secret = config["JWT_SECRET"]
jwt_algorithm = config["JWT_ALGORITHM"] or "HS256"