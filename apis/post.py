from fastapi import Depends, HTTPException, APIRouter
from db.db import get_session
from utils.auth import resolve_access_token
from sqlalchemy.orm import Session
import db.models as m
from sqlalchemy.sql import expression as sql_exp
from pydantic import BaseModel
import datetime
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
import re
from typing import Literal
from sqlalchemy.sql import func as sql_func
from sqlalchemy.dialects.postgresql import insert as pg_insert

router = APIRouter(prefix="/posts", tags=["posts"])


class GetPostResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    written_user_id: int
    board_id: int
    like_cnt: int

    class Config:
        orm_mode = True


@router.get("/{post_id}")
def get_post(
    post_id: int,
    session: Session = Depends(get_session),
):
    post: m.Post = session.execute(
        sql_exp.select(m.Post).where(m.Post.id == post_id)
    ).scalar_one_or_none()

    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="post not found")

    return GetPostResponse.from_orm(post)


class SearchPostRequest(BaseModel):
    # filter (query parameters)
    like_user_id: int | None
    written_user_id: int | None
    board_id: int | None
    # sort
    sort_by: Literal["created_at"] | Literal["updated_at"] | Literal[
        "written_user_id"
    ] = "created_at"
    sort_direction: Literal["asc"] | Literal["desc"] = "asc"
    # pagination
    offset: int = 0
    count: int = 20


class SearchPostResponse(BaseModel):
    posts: list[GetPostResponse]
    count: int


@router.post("/search")
def search_post(
    q: SearchPostRequest,
    session: Session = Depends(get_session),
):
    post_query = sql_exp.select(m.Post)

    if q.like_user_id is not None:
        post_query = post_query.join(m.Post.likes).where(
            m.Like.user_id == q.like_user_id
        )
    if q.written_user_id is not None:
        post_query = post_query.where(m.Post.written_user_id == q.written_user_id)
    if q.board_id is not None:
        post_query = post_query.where(m.Post.board_id == q.board_id)

    post_cnt: int = session.scalar(
        sql_exp.select(sql_func.count()).select_from(post_query)
    )
    # post_cnt: int = session.execute(
    #     sql_exp.select(sql_func.count()).select_from(post_query)
    # ).scalar_one_or_none()

    # sorting way1) dictionary
    sort_by_column = {
        "created_at": m.Post.created_at,
        "updated_at": m.Post.updated_at,
        "written_user_id": m.Post.written_user_id,
    }[q.sort_by]

    sort_exp = {
        "asc": sort_by_column.asc(),
        "desc": sort_by_column.desc(),
    }[q.sort_direction]

    post_query = post_query.order_by(sort_exp)

    # sorting way2) getattr() method
    # post_query = post_query.order_by(
    #     getattr(getattr(m.Post, q.sort_by), q.sort_direction)()
    # )
    # if q.sort_direction is "asc":
    #     post_query = post_query.order_by(getattr(m.Post, q.sort_by).asc())
    # else:
    #     post_query = post_query.order_by(getattr(m.Post, q.sort_by).desc())

    post_query = post_query.offset(q.offset).limit(q.count)
    posts = session.scalars(post_query).all()
    # posts = session.execute(post_query).scalars().all()

    return SearchPostResponse(
        posts=[GetPostResponse.from_orm(post) for post in posts],
        count=post_cnt,
    )


class PostPostRequest(BaseModel):
    title: str
    content: str
    board_id: int


class PostHashtagRequest(BaseModel):
    name: str


@router.post("/")
def create_post(
    q: PostPostRequest,
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    post = m.Post(
        title=q.title,
        content=q.content,
        board_id=q.board_id,
        written_user_id=user_id,
    )

    session.add(post)

    content = q.content
    pattern = "#([0-9a-zA-Z가-힣]*)"
    hashtags = re.compile(pattern).findall(content)  # type:list

    session.execute(
        pg_insert(m.Hashtag)
        .values([{"name": hashtag} for hashtag in hashtags])
        .on_conflict_do_nothing()
    )

    session.commit()


@router.put("/{post_id:int}")
def update_post(
    post_id: int,
    q: PostPostRequest,
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    post: m.Post | None = session.execute(
        sql_exp.select(m.Post).where(m.Post.id == post_id)
    ).scalar_one_or_none()

    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="post not found")

    if post.written_user_id != user_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="this is not your post"
        )

    post.title = q.title
    post.content = q.content

    session.add(post)
    session.commit()


@router.delete("/{post_id:int}")
def delete_post(
    post_id: int,
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    post: m.Post | None = session.execute(
        sql_exp.select(m.Post).where(m.Post.id == post_id)
    ).scalar_one_or_none()

    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="post not found")

    if post.written_user_id != user_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="this is not your post"
        )

    session.delete(post)
    session.commit()


@router.post("/{post_id:int}/like")
def like_post(
    post_id: int,
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    post: m.Post | None = session.execute(
        sql_exp.select(m.Post).where(m.Post.id == post_id)
    ).scalar_one_or_none()

    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="post not found")

    like: m.Like | None = session.execute(
        sql_exp.select(m.Like).where(
            (m.Like.post_id == post_id) & (m.Like.user_id == user_id)
        )
    ).scalar_one_or_none()

    if like is not None:
        return

    like = m.Like(
        post_id=post_id,
        user_id=user_id,
    )

    session.add(like)
    session.commit()


@router.delete("/{post_id:int}/like")
def like_delete(
    post_id: int,
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    post: m.Post | None = session.execute(
        sql_exp.select(m.Post).where(m.Post.id == post_id)
    ).scalar_one_or_none()

    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="post not found")

    like: m.Like | None = session.execute(
        sql_exp.select(m.Like).where(
            (m.Like.post_id == post_id) & (m.Like.user_id == user_id)
        )
    ).scalar_one_or_none()

    if like is None:
        return

    session.delete(like)
    session.commit()
