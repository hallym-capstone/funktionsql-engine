import os
import boto3

from pathlib import Path
from dotenv import load_dotenv


env_path = Path("config") / ".env"
load_dotenv(dotenv_path=env_path)


class ExecutionEngine:
    iam_client = None
    lambda_client = None

    @classmethod
    def initialize(cls):
        print("[*] initialized Execution Engine")

        cls.iam_client = boto3.client("iam")
        cls.lambda_client = boto3.client(
            "lambda",
            region_name="ap-northeast-2",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY")
        )

    @classmethod
    def consume_executable_query(cls):
        pass

    @classmethod
    def create_lambda_executable(cls, lambda_key: str, file: bytes):
        if cls.iam_client is None or cls.lambda_client is None:
            return

        role = cls.iam_client.get_role(RoleName="LambdaBasicExecution")
        response = cls.lambda_client.create_function(
            FunctionName=lambda_key,
            Runtime="python3.9",  # TODO: support other languages
            Role=role["Role"]["Arn"],
            Handler="lambda.lambda_handler",
            Code=dict(ZipFile=file),
            Timeout=300,
        )
        status = response["ResponseMetadata"]["HTTPStatusCode"]
        if status >= 200 and status < 300:
            return True
        return False

    @classmethod
    def construct_lambda_execution(cls):
        if cls.lambda_client is None:
            return
        response = cls.lambda_client.invoke(
            FunctionName="test",
            InvocationType="RequestResponse",
        )
        print(response["Payload"].read().decode("utf-8"))

    @classmethod
    def run_executable_query(cls):
        pass
