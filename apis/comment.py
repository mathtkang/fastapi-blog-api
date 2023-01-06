from fastapi import Depends, HTTPException, APIRouter
from db.db import get_session
from utils.auth import resolve_access_token, validate_user_role
from sqlalchemy.orm import Session
import db.models as m
from sqlalchemy.sql import expression as sql_exp
from pydantic import BaseModel, Field
import datetime
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from typing import Literal
from sqlalchemy.sql import func as sql_func

router = APIRouter(prefix="/posts/{post_id:int}/comments", tags=["comments"])


class GetCommentResponse(BaseModel):
    id: int
    content: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    user_id: int
    post_id: int
    parent_comment_id: int | None

    class Config:
        orm_mode = True


@router.get("/")
def get_all_comments(
    post_id: int,
    session: Session = Depends(get_session),
):
    comments: list[m.Comment] = (
        session.execute(sql_exp.select(m.Comment)).scalars().all()
    )
    return [GetCommentResponse.from_orm(comment) for comment in comments]


@router.get("/{comment_id:int}")
def get_comment(
    comment_id: int,
    session: Session = Depends(get_session),
):
    comment: m.Comment = session.execute(
        sql_exp.select(m.Comment).where(m.Comment.id == comment_id)
    ).scalar_one_or_none()

    if comment is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Comment with id {comment_id} not found",
        )

    return GetCommentResponse.from_orm(comment)


class SearchCommentRequest(BaseModel):
    # filter (query parameters)
    parent_comment_id: int | None
    written_user_id: int | None
    post_id: int | None
    # sort
    sort_by: Literal["created_at"] | Literal["updated_at"] | Literal[
        "written_user_id"
    ] = "created_at"
    sort_direction: Literal["asc"] | Literal["desc"] = "asc"
    # pagination
    offset: int = 0
    count: int = 5


class SearchCommentResponse(BaseModel):
    comments: list[SearchCommentRequest]
    count: int


# DONE: convert to get one comment
@router.post("/search")
def search_comments(
    q: SearchCommentRequest,
    session: Session = Depends(get_session),
):
    comment_query = sql_exp.select(m.Comment)

    if q.parent_comment_id is not None:
        comment_query = comment_query.where(
            m.Comment.parent_comment_id == q.parent_comment_id
        )
    if q.user_id is not None:
        comment_query = comment_query.where(m.Comment.user_id == q.written_user_id)
    if q.post_id is not None:
        comment_query = comment_query.where(m.Comment.post_id == q.post_id)

    comment_cnt: int = session.scalar(
        sql_exp.select(sql_func.count()).select_from(comment_query)
    )

    sort_by_column = {
        "created_at": m.Comment.created_at,
        "updated_at": m.Comment.updated_at,
        "written_user_id": m.Comment.user_id,
    }[q.sort_by]
    sort_exp = {
        "asc": sort_by_column.asc(),
        "desc": sort_by_column.desc(),
    }[q.sort_direction]

    comment_query = comment_query.order_by(sort_exp)

    comment_query = comment_query.offset(q.offset).limit(q.count)
    comments = session.execute(comment_query).scalars().all()

    return SearchCommentResponse(
        comments=[SearchCommentRequest.from_orm(comment) for comment in comments],
        count=comment_cnt
    )


class PostCommentRequest(BaseModel):
    content: str | None
    parent_comment_id: int | None = Field(default=None)


@router.post("/")
def create_comment(
    post_id: int,
    q: PostCommentRequest,
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    comment = m.Comment(
        post_id=post_id,
        user_id=user_id,
        content=q.content,
        parent_comment_id=q.parent_comment_id,
    )

    session.add(comment)
    session.commit()


@router.put("/{comment_id:int}")
def update_comment(
    post_id: int,
    comment_id: int,
    q: PostCommentRequest,
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    comment: m.Comment | None = session.execute(
        sql_exp.select(m.Comment).where(
            (m.Comment.id == comment_id)
            # & (m.Comment.user_id == user_id)
        )
    ).scalar_one_or_none()

    if comment is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="comment not found")

    if comment.user_id != user_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="this is not your comment"
        )

    comment.content = q.content

    session.add(comment)
    session.commit()


@router.delete("/{comment_id:int}")
def delete_comment(
    post_id: int,
    comment_id: int,
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    comment: m.Comment | None = session.execute(
        sql_exp.select(m.Comment).where(
            (m.Comment.id == comment_id)
            # & (m.Comment.user_id == user_id)
        )
    ).scalar_one_or_none()

    if comment is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="comment not found")

    if comment.user_id != user_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="this is not your comment"
        )

    session.delete(comment)
    session.commit()
