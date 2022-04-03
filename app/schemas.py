from pydantic import BaseModel


class ExecuteQuerySchema(BaseModel):
    query_selector: str
    function_name: str


class CreateDatabaseSchema(BaseModel):
    database_name: str
    api_key: str
