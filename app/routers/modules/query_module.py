from app.schemas import ExecuteQuerySchema


class QueryModule:

    @classmethod
    def execute_query(cls, data: ExecuteQuerySchema):
        pass

    @classmethod
    def validate_query_selector(cls, query_selector: str):
        pass

    @classmethod
    def validate_auth(cls, api_key: str):
        pass

    @classmethod
    def validate_database(cls, database_name: str, user_id: int):
        pass

    @classmethod
    def validate_function(cls, function_name: str, database_id: int):
        pass

    @classmethod
    def publish_to_runtime(cls):
        pass

    @classmethod
    def get_databases(cls, api_key: str):
        pass

    @classmethod
    def get_database(cls, database_name: str, api_key: str):
        pass

    @classmethod
    def get_functions(cls, database_name: str, api_key: str):
        pass

    @classmethod
    def get_function(cls, database_name: str, function_name: str, api_key: str):
        pass