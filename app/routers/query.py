from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from app.database import get_db
from app.schemas import CreateFunctionSchema, ExecuteQuerySchema, CreateDatabaseSchema
from app.routers.modules.auth_module import AuthModule
from app.routers.modules.query_module import QueryModule
from app.runtime.engine import RuntimeEngine


router = APIRouter()


# TODO: add error code
@router.post("/execute")
async def execute_query(
    data: ExecuteQuerySchema,
    user_id: int = Depends(AuthModule.validate_token),
    db: Session = Depends(get_db),
):
    return RuntimeEngine.consume_execute_request(data, user_id, db)


@router.post("/databases")
async def create_database(
    data: CreateDatabaseSchema,
    user_id: int = Depends(AuthModule.validate_token),
    db: Session = Depends(get_db),
):
    return QueryModule.create_database(data, user_id, db)


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


@router.post("/databases/{database_id}/functions")
async def create_function(
    database_id: int,
    data: CreateFunctionSchema,
    user_id: int = Depends(AuthModule.validate_token),
    db: Session = Depends(get_db),
):
    return RuntimeEngine.create_function(database_id, data, user_id, db)


@router.get("/databases/{database_id}/functions")
async def get_functions(
    database_id: int,
    user_id: int = Depends(AuthModule.validate_token),
    db: Session = Depends(get_db),
):
    return QueryModule.get_functions(database_id, user_id, db)


@router.get("/databases/{database_id}/functions/{function_id}")
async def get_function(
    database_id: int,
    function_id: int,
    user_id: int = Depends(AuthModule.validate_token),
    db: Session = Depends(get_db),
):
    return QueryModule.get_function(database_id, function_id, user_id, db)
