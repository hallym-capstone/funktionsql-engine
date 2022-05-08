from enum import Enum, IntEnum

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy import Column, ForeignKey, Integer, String, Text

from app.database import Base


class AuthType(IntEnum, Enum):
    BASIC = 0
    GOOGLE = 1
    KAKAO = 2
    NAVER = 3


class ExecutionResultType(IntEnum, Enum):
    ERROR = 0
    SUCCESS = 1


class ExecutionLanguage(IntEnum, Enum):
    PYTHON = 0
    NODEJS = 1
    JAVA = 2
    RUBY = 3
    GO = 4


class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False)
    password = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())


class Auth(Base):
    __tablename__ = "Auth"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    type = Column(Integer, nullable=False)
    auth_key = Column(String(256), unique=True, nullable=True)
    refresh_token = Column(String(256), nullable=False, default="")

    user = relationship(User)


class Database(Base):
    __tablename__ = "Databases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    name = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

    user = relationship(User)


class Function(Base):
    __tablename__ = "Functions"

    id = Column(Integer, primary_key=True, index=True)
    database_id = Column(Integer, ForeignKey(Database.id), nullable=False)
    name = Column(String(64), nullable=False)
    code = Column(Text())
    language = Column(Integer, nullable=False)
    lambda_key = Column(String(256), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

    database = relationship(Database)


class ExecutionHistory(Base):
    __tablename__ = "ExecutionHistory"

    id = Column(Integer, primary_key=True, index=True)
    function_id = Column(Integer, ForeignKey(Function.id), nullable=False)
    return_value = Column(String(256), nullable=False)
    type = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

    function = relationship(Function)
