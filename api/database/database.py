# TODO : read https://fastapi.tiangolo.com/tutorial/sql-databases/

# Put here the creation of the database
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./code_carbon.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# We will use the function declarative_base() that returns a class.
# Later we will inherit from this class to create each of the database models or classes (the ORM models)
Base = declarative_base()
