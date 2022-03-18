import os

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


env_path = Path("config") / ".env"
load_dotenv(dotenv_path=env_path)


DATABASE_USERNAME = os.getenv("MYSQL_USERNAME")
DATABASE_PASSWORD = os.getenv("MYSQL_PASSWORD")
DATABASE_HOST = os.getenv("MYSQL_HOST")
DATABASE_PORT = os.getenv("MYSQL_PORT")
DATABASE_NAME = os.getenv("MYSQL_DB")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
DBSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()
