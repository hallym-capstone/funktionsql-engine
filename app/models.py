from datetime import datetime
from enum import Enum, IntEnum

from sqlalchemy import JSON, Column, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship

from app.database import Base


class AuthType(IntEnum, Enum):
    NON_SOCIAL = 0
    GOOGLE = 1
    KAKAO = 2
    NAVER = 3


class ExecutionResultType(IntEnum, Enum):
    ERROR = 0
    SUCCESS = 1


class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False)
    password = Column(String(64), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now())


class Auth(Base):
    __tablename__ = "Auth"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    type = Column(Integer, nullable=False)
    auth_key = Column(String(256), unique=True, nullable=False)

    user = relationship("Users")


class Database(Base):
    __tablename__ = "Databases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    name = Column(String(64), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now())

    user = relationship("Users")


class Function(Base):
    __tablename__ = "Functions"

    id = Column(Integer, primary_key=True, index=True)
    database_id = Column(Integer, ForeignKey(Database.id), nullable=False)
    name = Column(String(64), nullable=False)
    lambda_key = Column(String(256), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now())
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.now())

    database = relationship("Databases")


class ExecutionHistory(Base):
    __tablename__ = "ExecutionHistory"

    id = Column(Integer, primary_key=True, index=True)
    function_id = Column(Integer, ForeignKey(Function.id), nullable=False)
    return_value = Column(String(256), nullable=False)
    type = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now())

    function = relationship("Functions")
