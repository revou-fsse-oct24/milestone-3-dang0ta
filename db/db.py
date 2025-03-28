import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker
from exceptions import ConfigurationError

db_conn = os.getenv("DB_CONN")
if not db_conn:
    raise ConfigurationError("DB_CONN is not set")

engine = create_engine(db_conn, echo=os.getenv('DEBUG', 'False').lower() in ['true', '1', 't'])
db_session = scoped_session(sessionmaker(
    autoflush=False, 
    bind=engine,
    autocommit=False))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    from .models import Account, User, Credential, Transactions, TransactionEntries
    Base.metadata.create_all(bind=engine)
