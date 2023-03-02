import datetime
import re
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import undefer
from sqlalchemy.sql import expression as sql_exp
from sqlalchemy.sql import func as sql_func
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from app.database import models as m
from app.utils.auth import resolve_access_token, validate_user_role
from app.utils.ctx import Context

router = APIRouter(prefix="/posts", tags=["posts"])


class GetPostResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    written_user_id: int | None
    board_id: int
    like_cnt: int

    class Config:
        orm_mode = True


# DONE
@router.get("/{post_id}")
async def get_post(
    post_id: int,
):
    post: m.Post = (
        await Context.current.db.session.execute(
            sql_exp.select(m.Post)
            .options(undefer(m.Post.like_cnt))  # after (추가됨)
            .where(m.Post.id == post_id)
        )
    ).scalar_one_or_none()

    if post is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"The post with {post_id} could not be found.",
        )

    return GetPostResponse.from_orm(post)


class SearchPostRequest(BaseModel):
    # filter (query parameters)
    like_user_id: int | None
    written_user_id: int | None
    board_id: int | None
    title: str | None
    # sort
    sort_by: Literal["created_at"] | Literal["updated_at"] = "created_at"
    sort_direction: Literal["asc"] | Literal["desc"] = "asc"
    # pagination
    offset: int = 0
    count: int = 20


class SearchPostResponse(BaseModel):
    posts: list[GetPostResponse]
    count: int


# DONE
@router.post("/search")
async def search_post(
    q: SearchPostRequest,
):
    # post_query = sql_exp.select(m.Post)
    post_query = sql_exp.select(m.Post).options(undefer(m.Post.like_cnt))  # after

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

    post_cnt: int = await Context.current.db.session.scalar(
        # sql_exp.select(sql_func.count()).select_from(post_query)
        sql_exp.select(sql_func.count()).select_from(post_query.subquery())  # after
    )

    # [sorting way1) dictionary]
    # sort_by_column = {
    #     "created_at": m.Post.created_at,
    #     "updated_at": m.Post.updated_at,
    # }[q.sort_by]

    # sort_exp = {
    #     "asc": sort_by_column.asc(),
    #     "desc": sort_by_column.desc(),
    # }[q.sort_direction]

    # post_query = post_query.order_by(sort_exp)

    # [sorting way2) getattr() method]
    post_query = post_query.order_by(
        getattr(getattr(m.Post, q.sort_by), q.sort_direction)()
    )
    if q.sort_direction == "asc":
        post_query = post_query.order_by(getattr(m.Post, q.sort_by).asc())
    else:
        post_query = post_query.order_by(getattr(m.Post, q.sort_by).desc())

    post_query = post_query.offset(q.offset).limit(q.count)
    posts = (await Context.current.db.session.scalars(post_query)).all()

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


# DONE: Hashtag 잘 적재되는지 확인 완료!
# (Context 앞에 await 안 붙여줘서 coroutine의 속성으로 인식 못한거임)
@router.post("/")
async def create_post(
    q: PostPostRequest,
    user_id: int = Depends(resolve_access_token),
):
    await validate_user_role(user_id, m.UserRoleEnum.Admin)

    post = m.Post(
        title=q.title,
        content=q.content,
        board_id=q.board_id,
        written_user_id=user_id,
    )

    Context.current.db.session.add(post)

    # create hashtag
    content = q.content
    pattern = "#([0-9a-zA-Z가-힣]*)"
    hashtags = re.compile(pattern).findall(content)  # type: list

    await Context.current.db.session.execute(
        pg_insert(m.Hashtag)
        .values([{"name": hashtag} for hashtag in hashtags])
        .on_conflict_do_nothing()  # This is only available with postgresql
    )
    """
    INSERT INTO hashtag
    VALUES (name) (
        'code',
        'camp',
    )
    ON CONFLICT DO NOTHING;
    """
    await Context.current.db.session.commit()

    return PostPostResponse(post_id=post.id)


# DONE
@router.put("/{post_id:int}")
async def update_post(
    post_id: int,
    q: PostPostRequest,
    user_id: int = Depends(resolve_access_token),
):
    await validate_user_role(user_id, m.UserRoleEnum.Admin)

    post: m.Post | None = await Context.current.db.session.scalar(
        sql_exp.select(m.Post).where(
            (m.Post.id == post_id) & (m.Post.board_id == q.board_id)
        )
    )

    if post is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="This post not found.",
        )

    if post.written_user_id != user_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="This is not your post. Therefore, it cannot be updated.",
        )

    post.title = q.title
    post.content = q.content

    Context.current.db.session.add(post)
    await Context.current.db.session.commit()


# DONE
@router.delete("/{post_id:int}")
async def delete_post(
    post_id: int,
    user_id: int = Depends(resolve_access_token),
):
    await validate_user_role(user_id, m.UserRoleEnum.Admin)

    post: m.Post | None = await Context.current.db.session.scalar(
        sql_exp.select(m.Post).where(m.Post.id == post_id)
    )

    if post is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="This post not found.",
        )

    if post.written_user_id != user_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="This is not your post. Therefore, it cannot be deleted.",
        )

    await Context.current.db.session.delete(post)
    await Context.current.db.session.commit()


class LikeResponse(BaseModel):
    post_id: int
    message: str | None


# DONE
@router.post("/{post_id:int}/like")
async def like_post(
    post_id: int,
    user_id: int = Depends(resolve_access_token),
):
    post: m.Post | None = await Context.current.db.session.scalar(
        sql_exp.select(m.Post).where(m.Post.id == post_id)
    )

    if post is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="This Post not found.",
        )

    like: m.Like | None = await Context.current.db.session.scalar(
        sql_exp.select(m.Like).where(
            (m.Like.post_id == post_id) & (m.Like.user_id == user_id)
        )
    )

    if like is not None:
        return LikeResponse(
            post_id=post_id, message="This post has already been liked."
        )

    like = m.Like(
        post_id=post_id,
        user_id=user_id,
    )

    Context.current.db.session.add(like)
    await Context.current.db.session.commit()

    return LikeResponse(post_id=like.post_id)


# DONE
@router.delete("/{post_id:int}/like")
async def like_delete(
    post_id: int,
    user_id: int = Depends(resolve_access_token),
):
    post: m.Post | None = await Context.current.db.session.scalar(
        sql_exp.select(m.Post).where(m.Post.id == post_id)
    )

    if post is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="This Post not found.",
        )

    like: m.Like | None = await Context.current.db.session.scalar(
        sql_exp.select(m.Like).where(
            (m.Like.post_id == post_id) & (m.Like.user_id == user_id)
        )
    )

    if like is None:
        return LikeResponse(
            post_id=post_id, message="This post has already been marked as unliked."
        )

    await Context.current.db.session.delete(like)
    await Context.current.db.session.commit()
