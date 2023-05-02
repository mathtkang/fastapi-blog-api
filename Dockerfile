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

# set env variables: for python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# for pip
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_ROOT_USER_ACTION=ignore 
    # # poetry:
    # POETRY_VERSION=1.3.2 \
    # POETRY_NO_INTERACTION=1 \
    # POETRY_VIRTUALENVS_CREATE=false \
    # POETRY_CACHE_DIR='/var/cache/pypoetry' \
    # POETRY_HOME='/usr/local'

RUN apt-get update -y
RUN apt-get install -y python3-pip

# # using poetry
# RUN pip3 install poetry
# RUN poetry install

# [install dependencies]
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# copy project requirement files here to ensure they will be cached.
# WORKDIR $PYSETUP_PATH
# COPY poetry.lock pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
# RUN poetry install --no-dev


# copy project
COPY . .

# CMD ["poetry", "run", "python3", "main.py"]
CMD ["python3", "main.py"]