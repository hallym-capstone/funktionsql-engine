import os
import secrets

from pathlib import Path
from dotenv import load_dotenv
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials


security = HTTPBasic()


env_path = Path("config") / ".env"
load_dotenv(dotenv_path=env_path)


def validate_credentials(credentials: HTTPBasicCredentials):
    correct_username = secrets.compare_digest(credentials.username, str(os.getenv("BASIC_AUTH_USERNAME")))
    correct_password = secrets.compare_digest(credentials.password, str(os.getenv("BASIC_AUTH_PASSWORD")))
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Invalid user credentials")
