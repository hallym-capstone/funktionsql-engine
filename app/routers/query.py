from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from app.database import get_db
from app.schemas import ExecuteQuerySchema, CreateDatabaseSchema
from app.routers.modules.query_module import QueryModule
from app.execution.engine import ExecutionEngine
from app.routers.modules.auth_module import AuthModule


router = APIRouter()


@router.post("/test")
async def test():
    return ExecutionEngine.construct_lambda_execution()


@router.post("/execute")
async def execute_query(data: ExecuteQuerySchema):
    return QueryModule.execute_query(data)


@router.post("/databases")
async def create_database(
    data: CreateDatabaseSchema,
    db: Session = Depends(get_db),
):
    return QueryModule.create_database(data, db)


@router.get("/databases")
async def get_databases(
    user_id: int = Depends(AuthModule.validate_token),
    db: Session = Depends(get_db),
):
    return QueryModule.get_databases(user_id, db)


@router.get("/databases/{database_id}")
async def get_database(
    database_id: int,
    user_id: int = Depends(AuthModule.validate_token),
    db: Session = Depends(get_db),
):
    return QueryModule.get_database(database_id, user_id, db)


@router.get("/databases/{database_id}/functions")
async def get_functions(database_id: int, api_key: str):
    return QueryModule.get_functions(database_id, api_key)


@router.get("/databases/{database_id}/functions/{function_id}")
async def get_function(database_id: int, function_id: int, api_key: str):
    return QueryModule.get_function(database_id, function_id, api_key)
