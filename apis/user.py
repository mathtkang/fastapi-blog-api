from fastapi import Depends, APIRouter, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from db.db import get_session
from utils.auth import resolve_access_token, validate_user_role
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db import models as m
from sqlalchemy.sql import expression as sql_exp
from utils.auth import generate_hashed_password, validate_hashed_password
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
import datetime
import jwt, time
from utils.blob import get_blob_client
from mypy_boto3_s3.client import S3Client
from utils.misc import get_random_string


router = APIRouter(prefix="/user", tags=["user"])


class GetUserInformationResponse(BaseModel):
    id: int
    email: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    role: int

    class Config:
        orm_mode = True




@router.get("/")
def get_all_users(
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    validate_user_role(user_id, m.UserRoleEnum.Admin, session)  # Admin = 25

    users: list[m.User] = session.execute(sql_exp.select(m.User)).scalars().all()

    return [GetUserInformationResponse.from_orm(user) for user in users]



@router.get("/me")
def get_my_information(
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    user: m.User | None = session.execute(
        sql_exp.select(m.User).where(m.User.id == user_id)
    ).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="User not found",
        )
    
    return GetUserInformationResponse.from_orm(user)


@router.post("/me")
# TODO: URL 생성 (다운로드받기)


@router.put("/me")
def update_my_profile(
    file: UploadFile,
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
    blob_client: S3Client = Depends(get_blob_client),
):
    '''
    파일스토리지
    1. session
    2. resolve access token (user_id)
    3. blob client
    4. 사용자의 입력(file)
    '''
    user: m.User | None = session.execute(
        sql_exp.select(m.User).where(m.User.id == user_id)
    ).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="User not found",
        )
    random_string = get_random_string(4)
    profile_file_key = f"profile_{user_id}_{random_string}"

    blob_client.upload_fileobj(file.file, "fastapi-practice", profile_file_key)

    user.profile_file_key = profile_file_key

    session.add(user)
    session.commit()


class PostRoleRequest(BaseModel):
    role: int
    user_id: int

@router.put("/role")
def change_user_role(
    q: PostRoleRequest,
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    validate_user_role(user_id, m.UserRoleEnum.Owner, session)

    user: m.User | None = session.execute(
        sql_exp.select(m.User).where(m.User.id == q.user_id)
    ).scalar_one_or_none()
    
    user.role = q.role

    session.add(user)
    session.commit()



class PostPasswordRequest(BaseModel):
    old_password: str
    new_password: str

@router.put("/change-password")
def change_password(
    q: PostPasswordRequest,
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    # 엑세스토큰을 갖고 있는 상태에서, 기존 비밀번호(확인 후)와 새로운 비밀번호를 받아서 변경
    user: m.User | None = session.execute(
        sql_exp.select(m.User).where(m.User.id == user_id)
    ).scalar_one_or_none()

    if not validate_hashed_password(q.old_password, user.password):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="password is wrong"
        )

    user.password = generate_hashed_password(q.new_password)

    session.add(user)
    session.commit()




@router.get("/likes")
def get_liked_post():
    pass