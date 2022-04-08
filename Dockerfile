FROM python:3.10.0-slim
RUN apt-get update \
  && apt-get install -y gcc \
  && apt-get clean

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT [ "uvicorn", "main:app", "--host=0.0.0.0" ]
