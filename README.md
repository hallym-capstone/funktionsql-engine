# funktionsql-engine

## Get Started

### Setup Virtual Environment
```
# create virtual environment
virtualenv venv

# activate virtual environment
source ./venv/bin/activate
```

### Install Dependencies
```
# install dependency requirements
pip3 install -r requirements.txt
```

### Run Server
```
uvicorn main:app --reload
```

### Run by Docker
```
# Build docker image
docker build -t funktionsql:0.0.1 .

# Run docker image
docker run -d -p 8000:8000 --name funktionsql --env-file ./config/.env funktionsql:0.0.1
```
