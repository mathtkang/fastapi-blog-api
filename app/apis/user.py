from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession as Session
from pydantic import BaseModel
from sqlalchemy.sql import expression as sql_exp
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)
import datetime
from app.utils.auth import resolve_access_token, validate_user_role
from app.database import models as m
from app.utils.auth import generate_hashed_password, validate_hashed_password
from app.utils.ctx import AppCtx


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


# A router that gets all users. However, '/all' is not recommended.
@router.get("/all")
async def get_all_users(
    user_id: int = Depends(resolve_access_token),
):
    validate_user_role(user_id, m.UserRoleEnum.Owner, AppCtx.current.db.session)  # Owner = 50

    users: list[m.User] = (
        await AppCtx.current.db.session.scalars(sql_exp.select(m.User))
    ).all()

    return [GetUserResponse.from_orm(user) for user in users]


# Rather than getting all users, it is better to return only one specified user.
@router.get("/{user_id}")
async def get_user(
    user_id: int = Depends(resolve_access_token),
):
    validate_user_role(user_id, m.UserRoleEnum.Admin, AppCtx.current.db.session)  # Admin = 25

    user: m.User = (
        await AppCtx.current.db.session.execute(
            sql_exp.select(m.User).where(m.User.id == user_id)
        )
    ).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"The user with {user_id} could not be found."
        )

    return GetUserResponse.from_orm(user)


# TODO: 유저 프로필 불러오기 (<- storage)
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
            detail="User not found",
        )

    if user.profile_file_key is not None:
        user.profile_file_url = AppCtx.current.s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": "fastapi-practice",
                "Key": user.profile_file_key,
            },
            ExpiresIn=60 * 60 * 24,
        )

    return GetUserResponse.from_orm(user)


class PutUserRequest(BaseModel):
    profile_file_key: str | None
    # 예) 기본프로필로 변경


# TODO: 유저 프로필 생성하기
@router.post("/me")
async def create_me(
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


# TODO: 유저 프로필 업데이트
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
    validate_user_role(user_id, m.UserRoleEnum.Owner,AppCtx.current.db.session)

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
