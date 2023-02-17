from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.sql import expression as sql_exp
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)
from typing import Literal
import datetime
from sqlalchemy.sql import func as sql_func
from app.utils.auth import resolve_access_token, validate_user_role
from app.database import models as m
from app.utils.auth import generate_hashed_password, validate_hashed_password
from app.utils.ctx import AppCtx
from app.utils.blob import get_image_url

router = APIRouter(prefix="/user", tags=["user"])


class GetUserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    role: int
    profile_file_url: str | None

    class Config:
        orm_mode = True


class SearchUserRequest(BaseModel):
    # filter (query parameters)
    email: str | None
    role: int | None
    # sort
    sort_by: Literal["created_at"] | Literal["updated_at"] = "created_at"
    sort_direction: Literal["asc"] | Literal["desc"] = "asc"
    # pagination
    offset: int = 0
    count: int = 20

class SearchUserResponse(BaseModel):
    users: list[GetUserResponse]
    count: int


# ING
@router.post("/search")
async def search_user(
    q: SearchUserRequest,
):
    user_query = sql_exp.select(m.User)

    if q.email is not None:
        user_query = user_query.where(m.User.email.ilike(q.email))
    if q.role is not None:
        user_query = user_query.where(m.User.role == q.role)

    user_cnt: int = await AppCtx.current.db.session.scalar(
        sql_exp.select(sql_func.count()).select_from(user_query)
    )

    sort_by_column = {
        "created_at": m.User.created_at,
        "updated_at": m.User.updated_at,
    }[q.sort_by]

    sort_exp = {
        "asc": sort_by_column.asc(),
        "desc": sort_by_column.desc(),
    }[q.sort_direction]

    user_query = user_query.order_by(sort_exp)

    user_query = user_query.offset(q.offset).limit(q.count)
    users = (await AppCtx.current.db.session.scalars(user_query)).all()

    return SearchUserResponse(
        users=[GetUserResponse.from_orm(user) for user in users],
        count=user_cnt,
    )





# A router that gets all users. However, '/all' is not recommended.
# @router.get("/all")
# async def get_all_users(
#     user_id: int = Depends(resolve_access_token),
# ):
#     validate_user_role(user_id, m.UserRoleEnum.Owner)  # Owner = 50

#     users: list[m.User] = (
#         await AppCtx.current.db.session.scalars(sql_exp.select(m.User))
#     ).all()

#     return [GetUserResponse.from_orm(user) for user in users]

# ^ Rather than getting all users, it is better to return only one specified user.
@router.get("/{user_id}")
async def get_user(
    user_id: int = Depends(resolve_access_token),
):
    await validate_user_role(user_id, m.UserRoleEnum.Admin)

    user: m.User = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.User).where(m.User.id == user_id)
    )

    if user is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"The user with {user_id} could not be found."
        )

    return GetUserResponse.from_orm(user)


@router.get("/me")
async def get_me(
    user_id: int = Depends(resolve_access_token),
):
    user: m.User | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.User).where(m.User.id == user_id)
    )

    if user is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail=f"The user with {user_id} could not be found."
        )
    
    return GetUserResponse.from_orm(user)
    # 만약 profile_file_url 가져와지지 않으면 'async-property' 찾아보기


class PutUserRequest(BaseModel):
    profile_file_key: str | None


@router.put("/me")
async def update_me(
    q: PutUserRequest,
    user_id: int = Depends(resolve_access_token),
):
    user: m.User | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.User).where(m.User.id == user_id)
    )

    if user is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="User not found",
        )

    user.profile_file_key = q.profile_file_key

    AppCtx.current.db.session.add(user)
    await AppCtx.current.db.session.commit()


class PostRoleRequest(BaseModel):
    role: int
    user_id: int


@router.put("/role")
async def change_user_role(
    q: PostRoleRequest,
    user_id: int = Depends(resolve_access_token),
):
    await validate_user_role(user_id, m.UserRoleEnum.Owner)

    user: m.User | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.User).where(m.User.id == q.user_id)
    )

    user.role = q.role

    AppCtx.current.db.session.add(user)
    await AppCtx.current.db.session.commit()


class PostPasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.put("/change-password")
async def change_password(
    q: PostPasswordRequest,
    user_id: int = Depends(resolve_access_token),
):
    user: m.User | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.User).where(m.User.id == user_id)
    )

    if not validate_hashed_password(q.old_password, user.password):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="password is wrong"
        )

    user.password = generate_hashed_password(q.new_password)

    AppCtx.current.db.session.add(user)
    await AppCtx.current.db.session.commit()
