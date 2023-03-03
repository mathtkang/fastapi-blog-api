# fastapi-practice
fastapi로 만든 blog 입니다.


## Set-up requirement

- python version >= 3.10

## Setting steps

0. `pip install pyenv poetry`
1. `pyenv virtualenv (python-version) fastapi-practice` > create virtual-env
3. `pyenv local fastapi-practice` > set python-version in virtual-env

## Set-up steps

1. `pyenv shell > activate virtualenv
2. `poetry update` or `poetry lock` > setting apply pyproject.toml
3. `python main.py` or `uvicorn main:app --reload` > start app

## Migration guide
1. alembic revision --autogenerate > make migration
2. alembic upgrade head > migrate
