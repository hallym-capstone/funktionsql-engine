import uvicorn

from fastapi import FastAPI, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.responses import JSONResponse

from app.auth import validate_credentials
from app.execution.engine import ExecutionEngine
from app.runtime.engine import RuntimeEngine
from app.runtime.scheduler import RuntimeScheduler

from app.routers.auth import router as auth_router
from app.routers.query import router as query_router


security = HTTPBasic()


app = FastAPI(title="FunktionsQL API", version="1.0.0", docs_url=None, redoc_url=None, openapi_url=None)
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


@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(credentials: HTTPBasicCredentials = Depends(security)):
    validate_credentials(credentials)
    return JSONResponse(get_openapi(title="BiHolder-View-API", version="1.2.0", routes=app.routes))


@app.get("/docs", include_in_schema=False)
async def get_documentation(credentials: HTTPBasicCredentials = Depends(security)):
    validate_credentials(credentials)
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.on_event("startup")
async def startup():
    RuntimeEngine.initialize()
    RuntimeScheduler.initialize()
    ExecutionEngine.initialize()


if __name__ == "__main__":
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s - " + log_config["formatters"]["access"]["fmt"]
    log_config["formatters"]["default"]["fmt"] = "%(asctime)s - {%(pathname)s:%(lineno)d} " + log_config["formatters"]["default"]["fmt"]
    uvicorn.run(app, log_config=log_config)
