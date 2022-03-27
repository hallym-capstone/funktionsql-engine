from fastapi import APIRouter

from app.schemas import ExecuteQuerySchema
from app.routers.modules.query_module import QueryModule


router = APIRouter()


@router.get("/execute")
async def execute_query(data: ExecuteQuerySchema):
    return QueryModule.execute_query(data)


@router.get("/databases")
async def get_databases(api_key: str):
    return QueryModule.get_databases(api_key)


@router.get("/databases/{database_id}")
async def get_database(database_id: int, api_key: str):
    return QueryModule.get_database(database_id, api_key)


@router.get("/databases/{database_id}/functions")
async def get_functions(database_id: int, api_key: str):
    return QueryModule.get_functions(database_id, api_key)


@router.get("/databases/{database_id}/functions/{function_id}")
async def get_function(database_id: int, function_id: int, api_key: str):
    return QueryModule.get_function(database_id, function_id, api_key)
