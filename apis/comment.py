from fastapi import Depends, HTTPException, APIRouter
from db.db import get_session
from utils.auth import resolve_access_token, validate_user_role
from sqlalchemy.orm import Session
import db.models as m
from sqlalchemy.sql import expression as sql_exp
from pydantic import BaseModel, Field
import datetime
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN


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
def read_comment(
    post_id: int,
    session: Session = Depends(get_session),
):
    comments: list[m.Comment] = session.execute(sql_exp.select(m.Comment)).scalars().all()
    
    return [GetCommentResponse.from_orm(comment) for comment in comments]

class PostCommentRequest(BaseModel):
    content: str | None
    parent_comment_id: int | None = Field(
        default=None
    )

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
        parent_comment_id=q.parent_comment_id
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