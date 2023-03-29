FROM python:3.10

# RUN apt-get update && apt-get install -y python-pip

COPY . /fastapi-blog
# 소스코드있을 때, 컨테이너에서 WORKDIR로 '소스코드 받을 directory(=code)'로 이동한다.
WORKDIR /fastapi-blog

# 1. requirements.txt 이용해서 설치하는 방법
# COPY ./requirements.txt /requirements.txt
# RUN pip install --no-cache-dir --upgrade -r /requirements.txt
# 2. poetry 설치 후, poetry로 python package를 설치하는 방법
RUN pip install poetry
RUN poetry install

CMD ["python3", "main.py"]