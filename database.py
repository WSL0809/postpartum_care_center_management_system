from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@db.yun.store:23778/postgres"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5432/postgres"

# DATABASE_URL = "sqlite:///mydatabase.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Session:
    """
    Provide a database session to the caller. The session should be closed after use.

    Yields:
        Session: A database session.

    Yields:
        None
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
