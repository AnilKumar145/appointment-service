# from sqlmodel import SQLModel, Session, create_engine
# from sqlalchemy.exc import SQLAlchemyError
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # PostgreSQL configuration
# POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
# POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "anil")
# POSTGRES_DB = os.getenv("POSTGRES_DB", "appointment_db")
# POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
# POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# try:
#     engine = create_engine(DATABASE_URL, pool_pre_ping=True)
#     print("✅ Database connection successful")
# except SQLAlchemyError as e:
#     print(f"❌ Database connection error: {str(e)}")
#     raise

# def get_session():
#     with Session(engine) as session:
#         yield session

# def create_db_and_tables():
#     try:
#         SQLModel.metadata.create_all(engine)
#         print("✅ Database tables created successfully")
#     except SQLAlchemyError as e:
#         print(f"❌ Error creating database tables: {str(e)}")
#         raise


import os

from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

# PostgreSQL configuration
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "anil")
POSTGRES_DB = os.getenv("POSTGRES_DB", "appointment_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")  # Changed from 'localhost' to 'db'
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# Create database URL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)  # Set echo=False in production


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
