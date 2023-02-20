from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.sql import expression as sql_exp
from pydantic import BaseModel
import datetime
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
import re
from typing import Literal
from sqlalchemy.sql import func as sql_func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.utils.auth import resolve_access_token, validate_user_role
from app.database import models as m
from app.utils.ctx import AppCtx

router = APIRouter(prefix="/hashtag", tags=["hashtag"])


class GetHashtagResponse(BaseModel):
    name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True

class SearchHashtagRequest(BaseModel):
    # filter (query parameters)
    name: str | None
    # sort
    sort_by: Literal["created_at"] | Literal["updated_at"] = "created_at"
    sort_direction: Literal["asc"] | Literal["desc"] = "asc"
    # pagination
    offset: int = 0
    count: int = 20


class SearchHashtagResponse(BaseModel):
    hashtags: list[GetHashtagResponse]
    count: int  # total number of hashtags (not saved to db)
    message: str | None


@router.post("/search")
async def search_hashtag(
    q: SearchHashtagRequest,
):
    hashtag_query = sql_exp.select(m.Hashtag)

    if q.name is not None:
        hashtag_query = hashtag_query.where(m.Hashtag.name.ilike(q.name))

    hashtag_cnt: int = await AppCtx.current.db.session.scalar(
        sql_exp.select(sql_func.count()).select_from(hashtag_query)
    )

    hashtag_query = hashtag_query.order_by(
        getattr(getattr(m.Hashtag, q.sort_by), q.sort_direction)()
    )
    if q.sort_direction == "asc":
        hashtag_query = hashtag_query.order_by(getattr(m.Hashtag, q.sort_by).asc())
    else:  # "desc"
        hashtag_query = hashtag_query.order_by(getattr(m.Hashtag, q.sort_by).desc())

    hashtag_query = hashtag_query.offset(q.offset).limit(q.count)
    hashtags = (await AppCtx.current.db.session.scalars(hashtag_query)).all()

    if hashtag_cnt == 0:
        return SearchHashtagResponse(
            hashtags=[GetHashtagResponse.from_orm(hashtag) for hashtag in hashtags],
            count=hashtag_cnt,
            message="Can't find a hashtag that meets the requirements. Please try again.",
        )
    else:
        return SearchHashtagResponse(
            hashtags=[GetHashtagResponse.from_orm(hashtag) for hashtag in hashtags],
            count=hashtag_cnt,
        )


#create <- at content of create_post 