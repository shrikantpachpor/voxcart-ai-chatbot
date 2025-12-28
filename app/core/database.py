from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config
import os
import logging


# Allow switching between PostgreSQL and SQLite for development
USE_SQLITE = config('USE_SQLITE', default='false').lower() in ('true', '1', 'yes')

if USE_SQLITE:
    # SQLite for development/testing
    DATABASE_URL = "sqlite:///./voxcart.db"
    logging.info(f"Using SQLite database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
else:
    # PostgreSQL for production
    DB_NAME = config('DB_NAME')
    DB_USER = config('DB_USER')
    DB_PASSWORD = config('DB_PASSWORD')
    DB_HOST = config('DB_HOST')
    DB_PORT = config('DB_PORT')

    # Disable GSS encryption (can help with some auth setups)
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?gssencmode=disable"
    logging.info(f"Using PostgreSQL database on {DB_HOST}:{DB_PORT}/{DB_NAME}")
    engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()