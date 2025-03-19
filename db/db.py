import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

engine = create_engine(os.getenv("DB_CONN"), echo=os.getenv('DEBUG', 'False').lower() in ['true', '1', 't'])
db_session = scoped_session(sessionmaker(
    autoflush=False, 
    bind=engine,
    autocommit=False))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    from .models import Account, User, Credential
    Base.metadata.create_all(bind=engine)
