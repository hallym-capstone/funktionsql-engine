import uuid

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session

from app.crud import create_function, get_database_by_id, get_function_by_database_id_and_name
from app.execution.engine import ExecutionEngine
from app.schemas import ExecuteQuerySchema


class RuntimeEngine:

    @classmethod
    def initialize(cls):
        print("[*] initialized Runtime Engine")

    @classmethod
    def create_function(cls, database_id: int, function_name: str, code: str, zip_file: bytes, user_id: int, db: Session):
        query_database = get_database_by_id(db, database_id)
        if not query_database:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"database with id={database_id} does not exist")

        if query_database.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403, detail=f"permission denied")

        query_function = get_function_by_database_id_and_name(db, database_id, function_name)
        if query_function:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"function name with '{function_name}' already exists")

        random_uuid = uuid.uuid4()
        lambda_key = f"{database_id}_{function_name}_{random_uuid}"
        is_created = ExecutionEngine.create_lambda_executable(lambda_key, zip_file)
        if not is_created:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"lambda executable creation error")

        return create_function(db, database_id, function_name, code, lambda_key)

    @classmethod
    def consume_execute_request(cls, database_id: int, data: ExecuteQuerySchema, user_id: int, db: Session):
        query_selector = data.query_selector
        function_name = data.function_name
        parameters = data.parameters

        query_database = get_database_by_id(db, database_id)
        if not query_database:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"database with id={database_id} does not exist")

        if query_database.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403, detail=f"permission denied")

        query_function = get_function_by_database_id_and_name(db, database_id, function_name)
        if not query_function:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"function does not exist(database_id={database_id}, name={function_name})")

        if query_selector == "RUN":
            is_succeeded, result = ExecutionEngine.run_lambda_executable(query_function.lambda_key, parameters)
            if not is_succeeded:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"lambda executable run failed({result})")
            return {"response": result}
        else:
            # TODO: support other query selectors
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"unsupported query selector received({query_selector})")

    @classmethod
    def consume_prepared_query(cls):
        pass

    @classmethod
    def abstract_relational_query(cls):
        pass

    @classmethod
    def publish_to_execution_engine(cls):
        pass
