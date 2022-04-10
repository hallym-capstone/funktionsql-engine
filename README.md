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
docker-compose up -d
```
