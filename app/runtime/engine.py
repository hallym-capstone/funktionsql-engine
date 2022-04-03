import uuid

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session

from app.crud import create_function, get_function_by_database_id_and_name
from app.execution.engine import ExecutionEngine


class RuntimeEngine:

    @classmethod
    def initialize(cls):
        print("[*] initialized Runtime Engine")

    @classmethod
    def create_function(cls, database_id: int, function_name: str, file: bytes, db: Session):
        # TODO: validate database
        random_uuid = uuid.uuid4()
        lambda_key = f"{database_id}_{function_name}_{random_uuid}"
        is_created = ExecutionEngine.create_lambda_executable(lambda_key, file)
        if not is_created:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"lambda executable creation error")

        return create_function(db, database_id, function_name, lambda_key)

    @classmethod
    def consume_execute_request(cls, database_id: int, function_name: str, query_selector: str, db: Session):
        # TODO: validate database
        query_function = get_function_by_database_id_and_name(db, database_id, function_name)
        if not query_function:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"function does not exist(database_id={database_id}, name={function_name})")

        if query_selector == "RUN":
            ExecutionEngine.run_lambda_executable(query_function.lambda_key)

    @classmethod
    def consume_prepared_query(cls):
        pass

    @classmethod
    def abstract_relational_query(cls):
        pass

    @classmethod
    def publish_to_execution_engine(cls):
        pass
