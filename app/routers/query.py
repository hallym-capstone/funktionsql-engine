from fastapi import APIRouter, Depends, File, status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session

from app.database import get_db
from app.schemas import ExecuteQuerySchema, CreateDatabaseSchema
from app.routers.modules.auth_module import AuthModule
from app.routers.modules.query_module import QueryModule
from app.runtime.engine import RuntimeEngine


router = APIRouter()


# TODO: add error code
# TODO: add comments
# TODO: add api docs
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


@router.post("/databases/{database_id}/execute")
async def execute_query(
    database_id: int,
    data: ExecuteQuerySchema,
    user_id: int = Depends(AuthModule.validate_token),
    db: Session = Depends(get_db),
):
    return RuntimeEngine.consume_execute_request(database_id, data, user_id, db)


@router.post("/databases/{database_id}/functions")
async def create_function(
    database_id: int,
    function_name: str,
    code_file: bytes = File(...),
    zip_file: bytes = File(...),
    user_id: int = Depends(AuthModule.validate_token),
    db: Session = Depends(get_db),
):
    code: str = ""
    try:
        code = code_file.decode("utf-8")
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="code_file decode error")
    return RuntimeEngine.create_function(database_id, function_name, code, zip_file, user_id, db)


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
