import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def get_engine():
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@localhost:5432/{DB_NAME}",
        echo=True,
    )

    return engine


def create_session():
    engine = get_engine()
    session = sessionmaker(bind=engine)

    return session
