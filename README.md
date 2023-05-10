# FastAPI-Blog

### 🚀 [서비스 바로가기](http://3.39.239.219/docs)

<br>

## 📃 프로젝트 개요
- 블로그 서비스의 API를 개발한 프로젝트입니다.

<br>

## ⚙️ 개발 환경
- ![macosm1 badge](https://img.shields.io/badge/MacOS%20M1-000000.svg?style=flat&logo=macOS&logoColor=white)
- ![Visual Studio Code badge](https://img.shields.io/badge/Visual%20Studio%20Code-007ACC.svg?style=flat&logo=Visual-Studio-Code&logoColor=white)
- ![github badge](https://img.shields.io/badge/GitHub-181717.svg?style=flat&logo=GitHub&logoColor=white)
- ![docker badge](https://img.shields.io/badge/Docker-2496ED.svg?style=flate&logo=Docker&logoColor=white)
- ![postman badge](https://img.shields.io/badge/postman-FF6C37?style=flat&logo=Postman&logoColor=white)
- ![swagger badge](https://img.shields.io/badge/Swagger-85EA2D.svg?style=flat&logo=Swagger&logoColor=black)

<br>

## 🛠 사용 기술
**Server**
- ![python badge](https://img.shields.io/badge/Python-3.10-%233776AB?&logo=python&logoColor=white)
- ![fastapi badge](https://img.shields.io/badge/FastAPI-0.89-109989?style=flat&logo=FastAPI&logoColor=white)
- ![Pydantic badge](https://img.shields.io/badge/Pydantic-1.10-109989?style=flat&logoColor=white)
- ![pyjwt badge](https://img.shields.io/badge/PYJWT-2.6-000000?style=flat&logo=JSON%20web%20tokens&logoColor=white)
- ![aws s3 badge](https://img.shields.io/badge/AWS-S3-FF9900?style=flat&logo=Amazon%20S3&logoColor=white)
- ![pytest badge](https://img.shields.io/badge/Pytest-7.2.2-0A9EDC.svg?style=flat&logo=Pytest&logoColor=white)

**Database**
- ![Postgres badge](https://img.shields.io/badge/postgres-14.5-%23316192.svg?style=flat&logo=postgresql&logoColor=white)
- ![SQLAlchemy badge](https://img.shields.io/badge/SQLAlchemy-2.0-109989?style=flat&logoColor=white)
- ![Alembic badge](https://img.shields.io/badge/Alembic-1.10-109989?style=flat&logoColor=white)

**Deploy**
- ![aws ec2 badge](https://img.shields.io/badge/AWS-EC2-%23FF9900?&logo=Amazon%20EC2&logoColor=white)
- ![docker badge](https://img.shields.io/badge/Docker-20.10.17-%232496ED?&logo=Docker&logoColor=white)
- ![nginx badge](https://img.shields.io/badge/Nginx-1.23.0-%23009639?logo=NGINX&locoColor=white)
- ![uvicorn badge](https://img.shields.io/badge/Uvicorn-0.20-499848.svg?style=flat&logo=Gunicorn&logoColor=white)

<br>

## 📙 API 명세서

### 👉 [📑 API Specification](https://sprinkle-piccolo-9fc.notion.site/API-Specification-fastapi-blog-c49db5e76866417ba4ed7a8bbbc50fa3)

<img width="1000" alt="API 명세서1" src="https://user-images.githubusercontent.com/51039577/233567324-b00c9c1b-0679-4b90-ab82-7d70091e60b1.png">
<img width="1000" alt="API 명세서2" src="https://user-images.githubusercontent.com/51039577/233567474-2cd57670-328b-4b19-a66d-96510ee55ec7.png">

<br>

## 📋 E-R Diagram
<img width="1000" alt="ERD" src="https://user-images.githubusercontent.com/51039577/233566785-e7423380-de51-4de2-b67d-b170168fd670.png">
❗️ 대댓글 구현 시 엔티티 구조 안에서 셀프조인을 참조하여 계층을 가지도록 구현했습니다.

<br>

## ✅ Test Case 
- pytest와 (async한 test code를 작성하기 위해) httpx를 사용하여 테스트 코드를 작성했습니다.
- S3를 이용하는 함수 테스트 시, monkeypatch를 사용해서 mocking된 함수를 대신 실행했습니다.
- 테스트 케이스를 작성함으로써, API에 수정사항이 생겼을 때 어떤 부분에서 이슈가 있는지 정확하게 확인할 수 있었습니다.
<img width="1000" alt="Test Case" src="https://user-images.githubusercontent.com/51039577/233592103-1baab1fd-344f-478f-8fea-35aa0eb4e12c.png">

<br>

## 🌍 배포 | [서비스 주소](http://3.39.239.219/docs)
AWS EC2 인스턴스에 Uvicorn, NginX를 사용하여 배포하였습니다.


<br>

## 📂 Directory Structure
<img width="300" alt="Directory Structure" src="https://user-images.githubusercontent.com/51039577/233581094-32b7f3a8-ec79-4dc7-80a8-fa471f01d703.png">

<br>

<!-- ## 🕸 System Architecture
<img width="1000" alt="System Architecture" src=""> -->





<br>
<br>
<br>
<br>

---

## Set-up requirement

- Python version >= 3.10
- Unix/Linux kernel (for uvloop)

## Setting steps

0. `pip install pyenv poetry`
1. `pyenv virtualenv (python-version) fastapi-blog` > create virtual-env
3. `pyenv local fastapi-blog` > set python-version in virtual-env

## Set-up steps

1. `pyenv shell` > activate virtualenv
2. `poetry update` or `poetry lock` > setting apply pyproject.toml
3. `python main.py` or `uvicorn main:app --reload` > start app

## Migration guide
1. `alembic revision --autogenerate` > make migration
2. `alembic upgrade head` > migrate


If you want more information  for alembic go to this [page](https://alembic.sqlalchemy.org/en/latest/)
