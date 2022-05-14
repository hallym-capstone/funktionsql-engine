import os
import uuid
import zipfile

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session

from app.crud import create_function, get_database_by_id, get_database_by_user_id_and_name, get_databases_by_user_id, get_function_by_database_id_and_name, get_functions_by_database_id, get_runtimeKey
from app.execution.engine import ExecutionEngine
from app.models import COMMON_SELECTORS, DATABASE_RELATED_SELECTORS, FUNCTION_RELATED_SELECTORS
from app.schemas import CreateFunctionSchema, ExecuteQuerySchema
from app.logging import logger


class RuntimeEngine:

    @classmethod
    def initialize(cls):
        logger.info("[*] initialized Runtime Engine")

    @classmethod
    def create_function(cls, database_id: int, data: CreateFunctionSchema, user_id: int, db: Session):
        code = data.code
        language = data.language
        function_name = data.function_name

        if not code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid code string received")
        if not function_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid function_name received")

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
        runtime_key, runtime_extension, runtime_handler = get_runtimeKey(language, lambda_key)

        code_file = open(f"{lambda_key}.{runtime_extension}", "w")
        code_file.write(data.code)
        code_file.close()

        zip_file = zipfile.ZipFile(f"{lambda_key}.zip", "w")
        zip_file.write(f"{lambda_key}.{runtime_extension}")
        zip_file.close()

        with open(f"{lambda_key}.zip", "rb") as read_zip_file:
            bytes_content = read_zip_file.read()

        try:
            is_created = ExecutionEngine.create_lambda_executable(lambda_key, bytes_content, runtime_key, runtime_handler)
            if not is_created:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"lambda executable creation error")
        except Exception as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

        os.remove(f"{lambda_key}.{runtime_extension}")
        os.remove(f"{lambda_key}.zip")
        return create_function(db, database_id, function_name, code, language.value, lambda_key)

    @classmethod
    def consume_execute_request(cls, database_id: int, data: ExecuteQuerySchema, user_id: int, db: Session):
        query_selector = data.query_selector.lower()
        query_target = data.query_target
        parameters = data.parameters

        if not query_selector:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid query_selector received")
        if not query_target:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid query_target received")

        # 공통 쿼리
        if query_selector in COMMON_SELECTORS:
            if query_target == "databases":
                query_databases = get_databases_by_user_id(db, user_id)
                return {"response": list(map(lambda db: db.name, query_databases))}
            elif query_target == "functions":
                query_functions = get_functions_by_database_id(db, database_id)
                return {"response": list(map(lambda fn: fn.name, query_functions))}
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"unsupported query target received({query_target})")

        # 데이터베이스 전용 쿼리
        elif query_selector in DATABASE_RELATED_SELECTORS:
            query_database = get_database_by_user_id_and_name(db, user_id, query_target)
            if not query_database:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"database with name={query_target} does not exist")

            if query_selector == "use":
                return {"response": query_database}
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"unsupported query selector received({query_selector})")

        # 함수 전용 쿼리
        elif query_selector in FUNCTION_RELATED_SELECTORS:
            query_database = get_database_by_id(db, database_id)
            if not query_database:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"database with id={database_id} does not exist")

            if query_database.user_id != user_id:
                raise HTTPException(status_code=status.HTTP_403, detail=f"permission denied")

            query_function = get_function_by_database_id_and_name(db, database_id, query_target)
            if not query_function:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"function does not exist(database_id={database_id}, name={query_target})")

            if query_selector == "run":
                is_succeeded, result = ExecutionEngine.run_lambda_executable(query_function.lambda_key, parameters)
                if not is_succeeded:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"lambda executable run failed({result})")
                return {"response": result}
            elif query_selector == "select":
                return {"response": query_function.code}
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"unsupported query selector received({query_selector})")

        # 지원되지 않는 쿼리
        else:
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
