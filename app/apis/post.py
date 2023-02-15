from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession as Session
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
async def get_post(
    post_id: int,
):
    post: m.Post = (
        await AppCtx.current.db.session.execute(
            sql_exp.select(m.Post).where(m.Post.id == post_id)
        )
    ).scalar_one_or_none()

    if post is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, 
            detail=f"The post with {post_id} could not be found."
        )

    return GetPostResponse.from_orm(post)


class SearchPostRequest(BaseModel):
    # filter (query parameters)
    like_user_id: int | None
    written_user_id: int | None
    board_id: int | None
    title: str | None
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
async def search_post(
    q: SearchPostRequest,
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
    if q.title is not None:
        post_query = post_query.where(m.Post.title.ilike(q.title))

    post_cnt: int = await AppCtx.current.db.session.scalar(
        sql_exp.select(sql_func.count()).select_from(post_query)
    )

    # [sorting way1) dictionary]
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

    # [sorting way2) getattr() method]
    # post_query = post_query.order_by(
    #     getattr(getattr(m.Post, q.sort_by), q.sort_direction)()
    # )
    # if q.sort_direction is "asc":
    #     post_query = post_query.order_by(getattr(m.Post, q.sort_by).asc())
    # else:
    #     post_query = post_query.order_by(getattr(m.Post, q.sort_by).desc())

    post_query = post_query.offset(q.offset).limit(q.count)
    posts = (await AppCtx.current.db.session.scalars(post_query)).all()

    return SearchPostResponse(
        posts=[GetPostResponse.from_orm(post) for post in posts],
        count=post_cnt,
    )


class PostPostRequest(BaseModel):
    title: str
    content: str
    board_id: int

class PostPostResponse(BaseModel):
    post_id: int


@router.post("/")
async def create_post(
    q: PostPostRequest,
    user_id: int = Depends(resolve_access_token),
):
    validate_user_role(user_id, m.UserRoleEnum.Admin, AppCtx.current.db.session)

    post = m.Post(
        title=q.title,
        content=q.content,
        board_id=q.board_id,
        written_user_id=user_id,
    )

    AppCtx.current.db.session.add(post)

    # create hashtag
    content = q.content
    pattern = "#([0-9a-zA-Z가-힣]*)"
    hashtags = re.compile(pattern).findall(content)  # type: list

    await AppCtx.current.db.session.execute(
        pg_insert(m.Hashtag)
        .values([{"name": hashtag} for hashtag in hashtags])
        .on_conflict_do_nothing()  # This is only available with postgresql
    )
    """
    INSERT INTO hastag
    VALUES (name) (
        'code',
        'camp',
    )
    ON CONFLICT DO NOTHING;
    """

    await AppCtx.current.db.session.commit()

    return PostPostResponse(post_id=post.id)

    """
    [아래 1,2 코드의 문제점]
    1. 너무 느림(전체를 다 탐색하면 안됨)
    모든 태그 비교가 아닌, 새롭게 받은 태그를 db와 비교해서 insert+update 를 해줘야한다.

    [처음 작성한 코드1]
    exist_hashtags: list[m.Hashtag] = (
        session.execute(
            sql_exp.select(m.Hashtag).where(m.Hashtag.name.in_(new_hashtags))
        )
        .scalars()
        .all()
    )

    for new_tag in new_hashtags:
        for exist_tag in exist_hashtags:
            if new_tag == exist_tag.name:
                continue
            tag = m.Hashtag(name=new_tag)
            session.add(tag)
    session.commit()

    [처음 작성한 코드2]
    for new_tag in new_hashtags:
        hashtag: m.Hashtag = session.execute(
            sql_exp.select(m.Hashtag).where(m.Hashtag.name == new_tag)
        ).scalar_one_or_none()

        if hashtag is not None:  # 기존에 같은 태그가 존재하면
            continue

        tag = m.Hashtag(name=new_tag)
        session.add(tag)
        session.commit()
    """

@router.put("/{post_id:int}")
async def update_post(
    post_id: int,
    q: PostPostRequest,
    user_id: int = Depends(resolve_access_token),
):
    validate_user_role(user_id, m.UserRoleEnum.Admin, AppCtx.current.db.session)

    post: m.Post | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.Post).where(m.Post.id == post_id)
    )

    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="post not found")

    if post.written_user_id != user_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="this is not your post"
        )

    post.title = q.title
    post.content = q.content

    AppCtx.current.db.session.add(post)
    await AppCtx.current.db.session.commit()


@router.delete("/{post_id:int}")
async def delete_post(
    post_id: int,
    user_id: int = Depends(resolve_access_token),
):
    validate_user_role(user_id, m.UserRoleEnum.Admin, AppCtx.current.db.session)

    post: m.Post | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.Post).where(m.Post.id == post_id)
    )

    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="post not found")

    if post.written_user_id != user_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="this is not your post"
        )

    await AppCtx.current.db.session.delete(post)
    await AppCtx.current.db.session.commit()


@router.post("/{post_id:int}/like")
async def like_post(
    post_id: int,
    user_id: int = Depends(resolve_access_token),
):
    post: m.Post | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.Post).where(m.Post.id == post_id)
    )

    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="post not found")

    like: m.Like | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.Like).where(
            (m.Like.post_id == post_id) & (m.Like.user_id == user_id)
        )
    )

    if like is not None:
        return

    like = m.Like(
        post_id=post_id,
        user_id=user_id,
    )

    AppCtx.current.db.session.add(like)
    await AppCtx.current.db.session.commit()


@router.delete("/{post_id:int}/like")
async def like_delete(
    post_id: int,
    user_id: int = Depends(resolve_access_token),
):
    post: m.Post | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.Post).where(m.Post.id == post_id)
    )

    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="post not found")

    like: m.Like | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.Like).where(
            (m.Like.post_id == post_id) & (m.Like.user_id == user_id)
        )
    )

    if like is None:
        return

    await AppCtx.current.db.session.delete(like)
    await AppCtx.current.db.session.commit()
