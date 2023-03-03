import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.sql import expression as sql_exp
from sqlalchemy.sql import func as sql_func
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from app.database import models as m
from app.utils.auth import resolve_access_token, validate_user_role
from app.utils.ctx import Context

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


# DONE
@router.get("/{comment_id:int}")
async def get_comment(
    post_id: int,
    comment_id: int,
):
    comment: m.Comment = await Context.current.db.session.scalar(
        sql_exp.select(m.Comment).where(
            (m.Comment.post_id == post_id) & (m.Comment.id == comment_id)
        )
    )

    if comment is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Comment not found.",
        )

    return GetCommentResponse.from_orm(comment)


class SearchCommentRequest(BaseModel):
    # filter (query parameters)
    content: str | None
    written_user_id: int | None
    parent_comment_id: int | None
    # sort
    sort_by: Literal["created_at"] | Literal["updated_at"] = "created_at"
    sort_direction: Literal["asc"] | Literal["desc"] = "asc"
    # pagination
    offset: int = 0
    count: int = 5


class SearchCommentResponse(BaseModel):
    comments: list[GetCommentResponse]
    count: int


# DONE
@router.post("/search")
async def search_comments(
    post_id: int,
    q: SearchCommentRequest,
):
    comment_query = sql_exp.select(m.Comment)

    if q.content is not None:
        comment_query = comment_query.where(m.Comment.content.ilike(q.content))
    if q.written_user_id is not None:
        comment_query = comment_query.where(
            m.Comment.written_user_id == q.written_user_id
        )
    if post_id is not None:
        comment_query = comment_query.where(m.Comment.post_id == post_id)
    if q.parent_comment_id is not None:
        comment_query = comment_query.where(
            m.Comment.parent_comment_id == q.parent_comment_id
        )

    comment_cnt: int = await Context.current.db.session.scalar(
        sql_exp.select(sql_func.count()).select_from(comment_query.subquery())
    )

    comment_query = comment_query.order_by(
        getattr(getattr(m.Comment, q.sort_by), q.sort_direction)()
    )
    if q.sort_direction == "asc":
        comment_query = comment_query.order_by(getattr(m.Comment, q.sort_by).asc())
    else:
        comment_query = comment_query.order_by(getattr(m.Comment, q.sort_by).desc())

    comment_query = comment_query.offset(q.offset).limit(q.count)
    comments = (await Context.current.db.session.scalars(comment_query)).all()

    return SearchCommentResponse(
        comments=[GetCommentResponse.from_orm(comment) for comment in comments],
        count=comment_cnt,
    )


class PostCommentRequest(BaseModel):
    content: str
    parent_comment_id: int | None  # optional


class PostCommentResponse(BaseModel):
    comment_id: int


# DONE
@router.post("/")
async def create_comment(
    post_id: int,
    q: PostCommentRequest,
    user_id: int = Depends(resolve_access_token),
):
    await validate_user_role(user_id, m.UserRoleEnum.Admin)

    comment = m.Comment(
        post_id=post_id,
        written_user_id=user_id,
        content=q.content,
        parent_comment_id=q.parent_comment_id,
    )

    Context.current.db.session.add(comment)
    await Context.current.db.session.commit()

    return PostCommentResponse(comment_id=comment.id)


# DONE
@router.put("/{comment_id:int}")
async def update_comment(
    post_id: int,
    comment_id: int,
    q: PostCommentRequest,
    user_id: int = Depends(resolve_access_token),
):
    await validate_user_role(user_id, m.UserRoleEnum.Admin)

    comment: m.Comment | None = await Context.current.db.session.scalar(
        sql_exp.select(m.Comment).where(
            (m.Comment.post_id == post_id) & (m.Comment.id == comment_id)
        )
    )

    if comment is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Comment not found.",
        )

    if comment.written_user_id != user_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="This is not your comment. Therefore, it cannot be updated.",
        )

    comment.content = q.content

    Context.current.db.session.add(comment)
    await Context.current.db.session.commit()


# DONE: parent_comment_id 삭제 시, children_comment도 삭제 확인 완료
@router.delete("/{comment_id:int}")
async def delete_comment(
    post_id: int,
    comment_id: int,
    user_id: int = Depends(resolve_access_token),
):
    await validate_user_role(user_id, m.UserRoleEnum.Admin)

    comment: m.Comment | None = await Context.current.db.session.scalar(
        sql_exp.select(m.Comment).where(
            (m.Comment.post_id == post_id) & (m.Comment.id == comment_id)
        )
    )

    if comment is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Comment not found.",
        )

    if comment.written_user_id != user_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="This is not your comment. Therefore, it cannot be deleted.",
        )

    await Context.current.db.session.delete(comment)
    await Context.current.db.session.commit()
