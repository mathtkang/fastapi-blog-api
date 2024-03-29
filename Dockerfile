FROM python:3.10

ENV PYTHONUNBUFFERED 1

# ref link : https://fastapi.tiangolo.com/ko/deployment/docker/#docker-cache

# /code 폴더 만들기
WORKDIR /code

# ./requirements.txt 를 /code/requirements.txt 로 복사
COPY ./requirements.txt /code/requirements.txt

# requirements.txt 를 보고 모듈 전체 설치(-r)
RUN pip install --no-cache-dir -r /code/requirements.txt

# 이제 app 에 있는 파일들을 /code/app 에 복사
COPY ./app /code/app

# 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]