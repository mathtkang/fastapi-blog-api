FROM python:3.10

FROM nginx
COPY nginx.conf /etc/nginx/nginx.conf


RUN apt-get update && apt-get install -y python-pip

COPY . /fastapi-practice
# 소스코드있을 때, 컨테이너에서 WORKDIR로 '소스코드 받을 directory(=code)'로 이동한다.
WORKDIR /fastapi-practice

# 1. requirements.txt 이용해서 설치하는 방법
# COPY ./requirements.txt /requirements.txt
# RUN pip install --no-cache-dir --upgrade -r /requirements.txt
# 2. poetry 설치 후, poetry로 python package를 설치하는 방법
RUN pip install poetry
COPY poetry.lock pyproject.toml /fastapi-practice/
RUN poetry lock


CMD ["python3", "main.py"]