from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession as Session
from sqlalchemy.sql import expression as sql_exp
from sqlalchemy.sql import func as sql_func
from pydantic import BaseModel, Field
import datetime
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from typing import Literal
from app.utils.auth import resolve_access_token, validate_user_role
from app.database import models as m
from app.utils.ctx import AppCtx

router = APIRouter(prefix="/posts/{post_id:int}/comments", tags=["comments"])


class GetCommentResponse(BaseModel):
    id: int
    content: str | None
    written_user_id: int
    post_id: int
    parent_comment_id: int | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True


@router.get("/{comment_id:int}")
async def get_comment(
    comment_id: int,
):
    comment: m.Comment = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.Comment).where(m.Comment.id == comment_id)
    )

    if comment is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Comment with id {comment_id} not found",
        )

    return GetCommentResponse.from_orm(comment)


class SearchCommentRequest(BaseModel):
    # filter (query parameters)
    content: str | None
    post_id: int | None
    written_user_id: int | None
    parent_comment_id: int | None
    # sort
    sort_by: Literal["created_at"] | Literal["updated_at"] | Literal[
        "written_user_id"
    ] = "created_at"
    sort_direction: Literal["asc"] | Literal["desc"] = "asc"
    # pagination
    offset: int = 0
    count: int = 5


class SearchCommentResponse(BaseModel):
    comments: list[GetCommentResponse]
    count: int


@router.post("/search")
async def search_comments(
    q: SearchCommentRequest,
):
    comment_query = sql_exp.select(m.Comment)

    if q.parent_comment_id is not None:
        comment_query = comment_query.where(
            m.Comment.parent_comment_id == q.parent_comment_id
        )
    if q.written_user_id is not None:
        comment_query = comment_query.where(m.Comment.written_user_id == q.written_user_id)
    if q.post_id is not None:
        comment_query = comment_query.where(m.Comment.post_id == q.post_id)
    if q.content is not None:
        comment_query = comment_query.where(m.Comment.content.ilike(q.content))

    comment_cnt: int = AppCtx.current.db.session.scalar(
        sql_exp.select(sql_func.count()).select_from(comment_query)
    )

    sort_by_column = {
        "created_at": m.Comment.created_at,
        "updated_at": m.Comment.updated_at,
        "written_user_id": m.Comment.written_user_id,
    }[q.sort_by]
    sort_exp = {
        "asc": sort_by_column.asc(),
        "desc": sort_by_column.desc(),
    }[q.sort_direction]

    comment_query = comment_query.order_by(sort_exp)

    comment_query = comment_query.offset(q.offset).limit(q.count)
    comments = (await AppCtx.current.db.session.scalars(comment_query)).all()

    return SearchCommentResponse(
        comments=[SearchCommentRequest.from_orm(comment) for comment in comments],
        count=comment_cnt,
    )


class PostCommentRequest(BaseModel):
    content: str
    parent_comment_id: int | None  # optional

class PostCommentResponse(BaseModel):
    comment_id: int


@router.post("/")
async def create_comment(
    post_id: int,
    q: PostCommentRequest,
    user_id: int = Depends(resolve_access_token),
):
    comment = m.Comment(
        post_id=post_id,
        written_user_id=user_id,
        content=q.content,
        parent_comment_id=q.parent_comment_id,
    )

    AppCtx.current.db.session.add(comment)
    await AppCtx.current.db.session.commit()

    return PostCommentResponse(comment_id=comment.id)


@router.put("/{comment_id:int}")
async def update_comment(
    comment_id: int,
    q: PostCommentRequest,
    user_id: int = Depends(resolve_access_token),
):
    comment: m.Comment | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.Comment).where(
            (m.Comment.id == comment_id)
        )
    )

    if comment is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="comment not found")

    if comment.written_user_id != user_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="this is not your comment"
        )

    comment.content = q.content

    AppCtx.current.db.session.add(comment)
    await AppCtx.current.db.session.commit()


@router.delete("/{comment_id:int}")
async def delete_comment(
    comment_id: int,
    user_id: int = Depends(resolve_access_token),
):
    comment: m.Comment | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.Comment).where(
            (m.Comment.id == comment_id)
        )
    )

    if comment is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="comment not found")

    if comment.written_user_id != user_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="this is not your comment"
        )

    await AppCtx.current.db.session.delete(comment)
    await AppCtx.current.db.session.commit()
