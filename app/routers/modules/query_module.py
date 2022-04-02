from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session

from app.models import Auth
from app.schemas import CreateDatabaseSchema, ExecuteQuerySchema
from app.crud import create_database, get_auth_by_api_key, get_database_by_user_id_and_name, get_databases_by_user_id


class QueryModule:

    @classmethod
    def execute_query(cls, data: ExecuteQuerySchema):
        pass

    @classmethod
    def validate_query_selector(cls, query_selector: str):
        pass

    @classmethod
    def validate_auth(cls, db: Session, api_key: str):
        query_auth = get_auth_by_api_key(db, api_key)
        if not query_auth:
            return None
        return query_auth

    @classmethod
    def validate_database(cls, database_name: str, user_id: int):
        pass

    @classmethod
    def validate_function(cls, function_name: str, database_id: int):
        pass

    @classmethod
    def publish_to_runtime(cls):
        pass

    @classmethod
    def create_database(cls, data: CreateDatabaseSchema, db: Session):
        query_auth: Auth = cls.validate_auth(db, data.api_key)
        if not query_auth:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"unauthorized user")

        query_database = get_database_by_user_id_and_name(db, query_auth.user_id, data.database_name)
        if query_database:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"database name duplication")

        return create_database(db, query_auth.user_id, data.database_name)

    @classmethod
    def get_databases(cls, user_id: int, db: Session):
        return get_databases_by_user_id(db, user_id)

    @classmethod
    def get_database(cls, database_id: int, api_key: str):
        pass

    @classmethod
    def get_functions(cls, database_id: int, api_key: str):
        pass

    @classmethod
    def get_function(cls, database_id: int, function_id: int, api_key: str):
        pass
