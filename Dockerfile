# pull the official docker image
FROM python:3.10

# RUN apt-get update -y
# RUN apt-get install -y python3-pip

# # COPY <호스트OS 파일 경로> <Docker 컨테이너 안에서의 경로>
# COPY . /fastapi-blog
# # 소스코드있을 때, 컨테이너에서 WORKDIR로 '소스코드 받을 directory(=code)'로 이동한다.
# WORKDIR /fastapi-blog

# RUN pip3 install poetry
# RUN poetry install

# CMD ["poetry", "run", "python3", "main.py"]



# set work directory
RUN mkdir /app
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y
RUN apt-get install -y python3-pip

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

CMD ["poetry", "run", "python3", "main.py"]