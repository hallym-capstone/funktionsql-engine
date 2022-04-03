from fastapi import APIRouter, Depends, File
from sqlalchemy.orm.session import Session

from app.database import get_db
from app.schemas import ExecuteQuerySchema, CreateDatabaseSchema
from app.routers.modules.auth_module import AuthModule
from app.routers.modules.query_module import QueryModule
from app.runtime.engine import RuntimeEngine


router = APIRouter()


@router.post("/databases")
async def create_database(
    data: CreateDatabaseSchema,
    db: Session = Depends(get_db),
):
    # TODO: validate auth
    return QueryModule.create_database(data, db)


@router.get("/databases")
async def get_databases(
    user_id: int = Depends(AuthModule.validate_token),
    db: Session = Depends(get_db),
):
    # TODO: validate auth
    return QueryModule.get_databases(user_id, db)


@router.get("/databases/{database_id}")
async def get_database(
    database_id: int,
    user_id: int = Depends(AuthModule.validate_token),
    db: Session = Depends(get_db),
):
    # TODO: validate auth
    return QueryModule.get_database(database_id, user_id, db)


@router.post("/databases/{database_id}/execute")
async def execute_query(
    database_id: int,
    data: ExecuteQuerySchema,
    db: Session = Depends(get_db),
):
    # TODO: validate auth
    return RuntimeEngine.consume_execute_request(database_id, data.function_name, data.query_selector, db)


@router.post("/databases/{database_id}/functions")
async def create_function(
    database_id: int,
    function_name: str,
    file: bytes = File(...),
    db: Session = Depends(get_db),
):
    # TODO: validate auth
    return RuntimeEngine.create_function(database_id, function_name, file, db)


@router.get("/databases/{database_id}/functions")
async def get_functions(database_id: int, db: Session = Depends(get_db)):
    return QueryModule.get_functions(database_id, db)


@router.get("/databases/{database_id}/functions/{function_id}")
async def get_function(database_id: int, function_id: int, db: Session = Depends(get_db)):
    return QueryModule.get_function(database_id, function_id, db)
