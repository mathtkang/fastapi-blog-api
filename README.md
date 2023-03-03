# fastapi-practice
fastapi로 만든 blog 입니다.





## 개발 환경

- MacOS M1
- Visual Studio Code
- GitHub
- Docker

**Server**
- Python 3.10
- FastAPI
- 

**Database**
- PostgreSQL

**Infra**
- AWS EC2
- AWS S3
- Docker


**Library**
- 

## System Architecture
![시스템 아키텍처]()


## Server Architecture
![아키텍처]()


## E-R Diagram
<img width="875" alt="스크린샷 2022-12-01 오후 4 31 42" src="https://user-images.githubusercontent.com/51039577/222684900-b9613635-aacd-4905-83bb-5a4586b4c2d8.png">


## 📑 API Specification
### [Api 명세서 보기](https://sprinkle-piccolo-9fc.notion.site/API-8f10817b6a1e41e085f356a24ca1c067)

## PURPOSE of Project



## Main function & 
### 1. 게시글 CRUD



### 2. 댓글 및 대댓글 구현
대댓글의 경우 엔티티 구조안에서 셀프조인을 참조하여 계층을 가지도록 구현했습니다.
















---

## Set-up requirement

- Python version >= 3.10
- Unix/Linux kernel (for uvloop)

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

If you want more information  for alembic go to this [page](https://alembic.sqlalchemy.org/en/latest/)
