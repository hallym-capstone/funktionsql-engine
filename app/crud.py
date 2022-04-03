from sqlalchemy import and_
from sqlalchemy.orm.session import Session

from app.models import Auth, Database, Function, User


def get_user_by_id(db: Session, id: int):
    return db.query(User).filter(User.id == id).first()


def get_auth_by_api_key(db: Session, api_key: str):
    return db.query(Auth).filter(Auth.auth_key == api_key).first()


def get_database_by_user_id_and_name(db: Session, user_id: int, name: str):
    return db.query(Database).filter(and_(Database.user_id == user_id, Database.name == name)).first()


def get_databases_by_user_id(db: Session, user_id: int):
    return db.query(Database).filter(Database.user_id == user_id).all()


def get_database_by_id_and_user_id(db: Session, id: int, user_id: int):
    return db.query(Database).filter(and_(Database.id == id, Database.user_id == user_id)).first()


def create_database(db: Session, user_id: int, name: str):
    query_database = Database(user_id=user_id, name=name)
    db.add(query_database)
    db.commit()
    db.refresh(query_database)
    return query_database


def create_function(db: Session, database_id: int, name: str, lambda_key: str):
    query_function = Function(database_id=database_id, name=name, lambda_key=lambda_key)
    db.add(query_function)
    db.commit()
    db.refresh(query_function)
    return query_function
