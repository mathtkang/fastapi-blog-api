FROM python:3.10

RUN apt-get update -y
RUN apt-get install -y python3-pip

COPY . /fastapi-blog
# 소스코드있을 때, 컨테이너에서 WORKDIR로 '소스코드 받을 directory(=code)'로 이동한다.
WORKDIR /fastapi-blog

RUN pip3 install poetry
RUN poetry install

CMD ["python3", "main.py"]