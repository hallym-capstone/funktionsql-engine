from sqlalchemy import and_
from sqlalchemy.orm.session import Session

from app.models import Auth, Database


def get_auth_by_api_key(db: Session, api_key: str):
    return db.query(Auth).filter(Auth.auth_key == api_key).first()


def get_database_by_user_id_and_name(db: Session, user_id: int, name: str):
    return db.query(Database).filter(and_(Database.user_id == user_id, Database.name == name)).first()


def create_database(db: Session, user_id: int, name: str):
    query_database = Database(user_id=user_id, name=name)
    db.add(query_database)
    db.commit()
    db.refresh(query_database)
    return query_database
