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
3. 태그 기반 검색 기능을 위해, 게시글이 삭제되면 connect_post_hashtag 테이블 안의 데이터도 함께 삭제 
    -> delete에서 내가 무언가 해주지 않아도, 자동으로 삭제되지 않나? relationship으로 이어져있으니까
'''


from fastapi import Depends, APIRouter
from db.db import get_session
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db import models as m
from sqlalchemy.sql import expression as sql_exp
from utils.auth import generate_hashed_password, validate_hashed_password
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST
import datetime


router = APIRouter(prefix="/hashtag", tags=["hashtag"])

class GetHashtagResponse(BaseModel):
    name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True

@router.get("/")
# TODO: 해시태그 전체 조회 -> 완료
def get_all_hashtag(
    session: Session = Depends(get_session),
):
    hashtags: list[m.Hashtag] = session.execute(sql_exp.select(m.Hashtag)).scalars().all()
    return [GetHashtagResponse.from_orm(hashtag) for hashtag in hashtags]


@router.get("/{hashtag_id:int}")
def get_hashtag(
    hashtag_id: int,
):
    pass
# 특정 해시태그에 대한 데이터(연관된 post) 가져오기
# 특정 해시태그가 있는 가장 인기있는 게시글 가져오기 (like 와 합쳐서)