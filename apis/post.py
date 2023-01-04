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


@router.get("/")
def read_post(
    session: Session = Depends(get_session),
    # user_id: int = Depends(resolve_access_token) | None
):
    posts: list[m.Post] = session.execute(sql_exp.select(m.Post)).scalars().all()
    
    return [GetPostResponse.from_orm(post) for post in posts]  # upgrade할 예정


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
    session.commit()

    # TODO: hashtag 리스트로 전달 -> test 완료
    content=q.content
    pattern = '#([0-9a-zA-Z가-힣]*)'
    new_hashtags = re.compile(pattern).findall(content)  # type:list

    exist_hashtags: list[m.Hashtag] = session.execute(sql_exp.select(m.Hashtag)).scalars().all()

    # for new_tag in new_hashtags:
    #     for exist_tag in exist_hashtags:
    #         if new_tag == exist_tag.name:
    #             continue
    #         tag = m.Hashtag(name=new_tag)
    #         session.add(tag)
    # session.commit()

    for new_tag in new_hashtags:
        hashtag: m.Hashtag = session.execute(
            sql_exp.select(m.Hashtag).where(m.Hashtag.name == new_tag)
        ).scalar_one_or_none()
        
        if hashtag is not None:  # 기존에 같은 태그가 존재하면
            continue

        tag = m.Hashtag(name=new_tag)
        session.add(tag)
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
