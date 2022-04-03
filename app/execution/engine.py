import os
import boto3

from pathlib import Path
from dotenv import load_dotenv


env_path = Path("config") / ".env"
load_dotenv(dotenv_path=env_path)


class ExecutionEngine:

    @classmethod
    def initialize(cls):
        print("[*] initialized Execution Engine")

    @classmethod
    def consume_executable_query(cls):
        pass

    @classmethod
    def construct_lambda_execution(cls):
        lambda_client = boto3.client(
            "lambda",
            region_name="ap-northeast-2",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY")
        )
        response = lambda_client.invoke(
            FunctionName="test",
            InvocationType="RequestResponse",
        )
        print(response["Payload"].read().decode("utf-8"))

    @classmethod
    def run_executable_query(cls):
        pass
