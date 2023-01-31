from fastapi import Depends, APIRouter, HTTPException
from app.database.db import get_session
from app.utils.auth import resolve_access_token, validate_user_role
from sqlalchemy.ext.asyncio import AsyncSession as Session
from pydantic import BaseModel
from app.database import models as m
from sqlalchemy.sql import expression as sql_exp
from app.utils.auth import generate_hashed_password, validate_hashed_password
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
)
import datetime
from mypy_boto3_s3.client import S3Client
from app.utils.blob import get_blob_client


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


# 추천하지 않음
@router.get("/all")
async def get_all_users(
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    validate_user_role(user_id, m.UserRoleEnum.Admin, session)  # Admin = 25

    users: list[m.User] = (
        await session.scalars(sql_exp.select(m.User))
    ).all()

    return [GetUserResponse.from_orm(user) for user in users]


# TODO: 유저 프로필 불러오기 (<- storage)
@router.get("/me")
async def get_me(
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
    blob_client: S3Client = Depends(get_blob_client),
):
    user: m.User | None = await session.scalar(
        sql_exp.select(m.User).where(m.User.id == user_id)
    )

    if user is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="User not found",
        )

    if user.profile_file_key is not None:
        user.profile_file_url = blob_client.generate_presigned_url(
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
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    # user: m.User | None = await session.scalar(
    #     sql_exp.select(m.User).where(m.User.id == user_id)
    # )

    # if user is None:
    #     raise HTTPException(
    #         status_code=HTTP_403_FORBIDDEN,
    #         detail="User not found",
    #     )

    # user.profile_file_key = q.profile_file_key

    # session.add(user)
    # await session.commit()
    pass

# TODO: 유저 프로필 업데이트
@router.put("/me")
async def update_me(
    q: PutUserRequest,
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    user: m.User | None = await session.scalar(
        sql_exp.select(m.User).where(m.User.id == user_id)
    )

    if user is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="User not found",
        )

    user.profile_file_key = q.profile_file_key

    session.add(user)
    await session.commit()


class PostRoleRequest(BaseModel):
    role: int
    user_id: int


@router.put("/role")
async def change_user_role(
    q: PostRoleRequest,
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    validate_user_role(user_id, m.UserRoleEnum.Owner, session)

    user: m.User | None = await session.scalar(
        sql_exp.select(m.User).where(m.User.id == q.user_id)
    )

    user.role = q.role

    session.add(user)
    await session.commit()


class PostPasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.put("/change-password")
async def change_password(
    q: PostPasswordRequest,
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    user: m.User | None = await session.scalar(
        sql_exp.select(m.User).where(m.User.id == user_id)
    )

    if not validate_hashed_password(q.old_password, user.password):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="password is wrong"
        )

    user.password = generate_hashed_password(q.new_password)

    session.add(user)
    await session.commit()
