from fastapi import APIRouter

from app.schemas import ExecuteQuerySchema
from app.routers.modules.query_module import QueryModule


router = APIRouter()


@router.get("/execute")
async def execute_query(data: ExecuteQuerySchema):
    return QueryModule.execute_query(data)
