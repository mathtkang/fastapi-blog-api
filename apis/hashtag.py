'''
[insert or ignore]
sql: 
on_confilct do nothing -> insert or ignore
do update -> upsert (update+insert)


[해시태그 기능 구현 로직]
1. post를 생성하는 동시에 content 필드를 가져와 정규식을 활용하여 해시태그 리스트로 전달
    ➡️ '#' 기준으로 추출
2. 해시태그 리스트의 값이 기존에 존재하는지 확인 후 upsert
    ➡️ 기존 hashtag 테이블에 존재하지 않는 해시태그라면 hashtag와 connect_post_hashtag 테이블 모두 추가
    ➡️ 기존에 존재하는 해시태그라면, connect_post_hashtag 테이블에만 추가
3. hashtag 테이블의 count 필드 값을 1 증가시킨다. -> 쿼리로 구해야함!
4. 태그 기반 검색 기능을 위해, 게시글이 삭제되면 connect_post_hashtag 테이블 안의 데이터도 함께 삭제
'''


from fastapi import Depends, APIRouter, HTTPException
from db.db import get_session
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db import models as m
from sqlalchemy.sql import expression as sql_exp
from utils.auth import generate_hashed_password, validate_hashed_password
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST
import jwt, time


router = APIRouter(prefix="/hashtag", tags=["hashtag"])


# 해시태그 리스트 만들기 (in post)
# 해시태그 리스트의 값이 기존에 존재하는지 확인 후 upsert 하기 (in post)


# 특정 해시태그에 대한 데이터(연관된 post, count 갯수) 가져오기
# 해시태크 전체 조회
# 특정 해시태크가 있는 가장 인기있는 게시글 가져오기 (like 와 합쳐서)