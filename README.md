# payback_recruitment

To install all requirements you need, first create and activate environment:
```shell
python -m venv .venv

. .venv/bin/activate
# for Windows users
source .venv/Scripts/activate
```
Then install packages:
```shell
pip install --upgrade pip && pip install -e .[dev]
```

If you want to run the tests, use:
```shell
pytest

# or 
pytest tests/
```
To run the fastapi application in docker container, ensure your docker is running
```shell
docker --help
```
If you want to run the application with default env variables, just run:
```shell
docker compose up -d --build

# or if you have deprecated docker-compose version
docker-compose up -d --build
```

otherwise, create a copy `.env` file from `.env-template` file, make you changes and run docker compose
```shell
cp .env-template .env
```

API docs: http://127.0.0.1:8000/docs
