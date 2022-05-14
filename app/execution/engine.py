import os
import json
import boto3

from pathlib import Path
from dotenv import load_dotenv

from app.logging import logger


env_path = Path("config") / ".env"
load_dotenv(dotenv_path=env_path)


class ExecutionEngine:
    iam_client = None
    lambda_client = None

    @classmethod
    def initialize(cls):
        logger.info("[*] initialized Execution Engine")

        cls.iam_client = boto3.client(
            "iam",
            region_name="ap-northeast-2",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        )
        cls.lambda_client = boto3.client(
            "lambda",
            region_name="ap-northeast-2",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        )

    @classmethod
    def create_lambda_executable(cls, lambda_key: str, file: bytes, runtime_key: str, runtime_handler: str):
        if cls.iam_client is None or cls.lambda_client is None:
            return False

        try:
            role = cls.iam_client.get_role(RoleName="LambdaBasicExecution")
            response = cls.lambda_client.create_function(
                FunctionName=lambda_key,
                Runtime=runtime_key,
                Role=role["Role"]["Arn"],
                Handler=runtime_handler,
                Code=dict(ZipFile=file),
                Timeout=300,
            )
            status = response["ResponseMetadata"]["HTTPStatusCode"]
            if status >= 200 and status < 300:
                return True
            return False
        except Exception as err:
            raise err

    @classmethod
    def run_lambda_executable(cls, lambda_key: str, parameters: dict = None):
        if cls.lambda_client is None:
            return

        try:
            if parameters:
                lambda_response = cls.lambda_client.invoke(
                    FunctionName=lambda_key,
                    InvocationType="RequestResponse",
                    LogType="Tail",
                    Payload=json.dumps(parameters),
                )
            else:
                lambda_response = cls.lambda_client.invoke(
                    FunctionName=lambda_key,
                    InvocationType="RequestResponse",
                    LogType="Tail",
                )
        except Exception as err:
            raise err

        if lambda_response:
            result = json.loads(lambda_response["Payload"].read().decode("utf-8"))
            if not result:
                return True, "null"

            if "errorMessage" in result:
                return False, result["errorMessage"]
            else:
                return True, result
        else:
            return True, "null"
