FROM python:3.10

ENV PYTHONUNBUFFERED 1

# 'mkdir app'이라는 명령어 실행
RUN mkdir /app
# 'cd app': 만들어진 'app' 폴더에 들어감
WORKDIR /app

# update & install
RUN apt-get update && apt-get install -y \
    python3-pip
    # nginx

# Copy files: COPY <호스트OS 파일 경로> <Docker 컨테이너 안에서의 경로>
COPY pyproject.toml /app/pyproject.toml


# (여기까지, app 폴더에는 pyproject.toml 만 존재한다!)


# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN export PATH="/home/ubuntu/.local/bin:$PATH"


# poetry init 은 아니다! 이미 pyproject.toml이 있으니까
# poetry install 로 가상환경을 설치한다.
RUN poetry install
# poetry shell 로 가상환경에 들어간다.
RUN poetry shell

CMD ["python3", "main.py"]




# # COPY <호스트OS 파일 경로> <Docker 컨테이너 안에서의 경로>
# COPY . /fastapi-blog
# # 소스코드있을 때, 컨테이너에서 WORKDIR로 '소스코드 받을 directory(=code)'로 이동한다.
# WORKDIR /fastapi-blog







# Install packages
# RUN pip install --upgrade pip
# RUN pip install -r requirements.txt








# poetry 하는건 일단 대기!

# ENV YOUR_ENV=${YOUR_ENV} \
#   PYTHONFAULTHANDLER=1 \
#   PYTHONUNBUFFERED=1 \

#   PYTHONHASHSEED=random \
#   PIP_NO_CACHE_DIR=off \
#   PIP_DISABLE_PIP_VERSION_CHECK=on \
#   PIP_DEFAULT_TIMEOUT=100 \
#   POETRY_VERSION=1.0.0


# # 환경만들어주기

# # Install dependencies
# RUN apt-get update && apt-get install -y \
#     software-properties-common \
#     curl \
#     python3.10 \
#     python3-pip

# # System deps:      # 이건 맞는듯!
# RUN pip install "poetry==$POETRY_VERSION"

# # Copy only requirements to cache them in docker layer
# WORKDIR /code
# COPY poetry.lock pyproject.toml /code/

# # Project initialization:
# RUN poetry config virtualenvs.create false \
#   && poetry install $(test "$YOUR_ENV" == production && echo "--no-dev") --no-interaction --no-ansi

# # Creating folders, and files for a project:
# COPY . /code
