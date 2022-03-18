from fastapi import APIRouter, Depends


router = APIRouter()


@router.get("/execute")
async def execute_query():
    pass
