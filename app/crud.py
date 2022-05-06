from typing import Union
from sqlalchemy import and_
from sqlalchemy.orm.session import Session

from app.models import Auth, AuthType, Database, ExecutionLanguage, Function, User


def get_user_by_id(db: Session, id: int):
    return db.query(User).filter(User.id == id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_auth_by_user_id(db: Session, user_id: int):
    return db.query(Auth).filter(Auth.user_id == user_id).first()


def get_auth_by_api_key(db: Session, api_key: str):
    return db.query(Auth).filter(Auth.auth_key == api_key).first()


def update_auth_refresh_token_by_user_id(db: Session, user_id: int, refresh_token: str):
    db.query(Auth).filter(Auth.user_id == user_id).update({Auth.refresh_token: refresh_token})


def get_database_by_id(db: Session, id: int):
    return db.query(Database).filter(Database.id == id).first()


def get_database_by_user_id_and_name(db: Session, user_id: int, name: str):
    return db.query(Database).filter(and_(Database.user_id == user_id, Database.name == name)).first()


def get_databases_by_user_id(db: Session, user_id: int):
    return db.query(Database).filter(Database.user_id == user_id).all()


def get_database_by_id_and_user_id(db: Session, id: int, user_id: int):
    return db.query(Database).filter(and_(Database.id == id, Database.user_id == user_id)).first()


def get_function_by_id(db: Session, id: int):
    return db.query(Function).filter(Function.id == id).first()


def get_functions_by_database_id(db: Session, database_id: int):
    return db.query(Function).filter(Function.database_id == database_id).all()


def get_function_by_database_id_and_name(db: Session, database_id: int, name: str):
    return db.query(Function).filter(and_(Function.database_id == database_id, Function.name == name)).first()


def create_user(db: Session, username: str, hashed_password: str):
    query_user = User(username=username, password=hashed_password)
    db.add(query_user)
    db.flush()
    return query_user


def create_auth(db: Session, user_id: int, type: AuthType, auth_key: Union[str, None], refresh_token: str):
    query_auth = Auth(user_id=user_id, type=type, auth_key=auth_key, refresh_token=refresh_token)
    db.add(query_auth)
    db.flush()
    return query_auth


def create_database(db: Session, user_id: int, name: str):
    query_database = Database(user_id=user_id, name=name)
    db.add(query_database)
    db.commit()
    db.refresh(query_database)
    return query_database


def create_function(db: Session, database_id: int, name: str, code: str, language: ExecutionLanguage, lambda_key: str):
    query_function = Function(database_id=database_id, name=name, code=code, language=language, lambda_key=lambda_key)
    db.add(query_function)
    db.commit()
    db.refresh(query_function)
    return query_function
