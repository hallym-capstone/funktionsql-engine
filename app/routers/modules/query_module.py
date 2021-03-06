from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session

from app.schemas import CreateDatabaseSchema, ExecuteQuerySchema
from app.crud import (
    create_database, get_auth_by_api_key, get_database_by_id, get_database_by_id_and_user_id,
    get_database_by_user_id_and_name, get_databases_by_user_id, get_function_by_id, get_functions_by_database_id,
)


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
    def create_database(cls, data: CreateDatabaseSchema, user_id: int, db: Session):
        query_database = get_database_by_user_id_and_name(db, user_id, data.database_name)
        if query_database:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"database name duplication")

        return create_database(db, user_id, data.database_name)

    @classmethod
    def get_databases(cls, user_id: int, db: Session):
        return get_databases_by_user_id(db, user_id)

    @classmethod
    def get_database(cls, database_id: int, user_id: int, db: Session):
        query_database = get_database_by_id_and_user_id(db, database_id, user_id)
        if not query_database:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"database not found")
        return query_database

    @classmethod
    def get_functions(cls, database_id: int, user_id: int, db: Session):
        query_database = get_database_by_id(db, database_id)
        if not query_database:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"database with id={database_id} does not exist")

        if query_database.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403, detail=f"permission denied")

        return get_functions_by_database_id(db, database_id)

    @classmethod
    def get_function(cls, database_id: int, function_id: int, user_id: int, db: Session):
        query_database = get_database_by_id(db, database_id)
        if not query_database:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"database with id={database_id} does not exist")

        if query_database.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403, detail=f"permission denied")

        query_function = get_function_by_id(db, function_id)
        if not query_function:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"function with id={function_id} does not exist")

        return query_function
