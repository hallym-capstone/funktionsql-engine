from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.execution.engine import ExecutionEngine
from app.runtime.engine import RuntimeEngine
from app.runtime.scheduler import RuntimeScheduler

from app.routers.auth import router as auth_router
from app.routers.query import router as query_router


app = FastAPI(title="FunktionsQL API", version="1.0.0")
app.include_router(auth_router, prefix="/auth")
app.include_router(query_router, prefix="/query")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def healthcheck():
    return {"status": True}


@app.on_event("startup")
async def startup():
    RuntimeEngine.initialize()
    RuntimeScheduler.initialize()
    ExecutionEngine.initialize()
