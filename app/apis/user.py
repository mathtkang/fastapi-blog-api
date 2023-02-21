from fastapi import Depends, APIRouter, HTTPException, UploadFile
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
from app.database import models as m
from app.utils.auth import (
    resolve_access_token, 
    validate_user_role,
    generate_hashed_password, 
    validate_hashed_password,
    validate_email_exist,
)
from app.utils.blob import upload_profile_img, get_image_url
from app.utils.ctx import AppCtx

router = APIRouter(prefix="/user", tags=["user"])


DEFAULT_BUCKET_NAME = "fastapi-practice"


class GetUserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    role: int
    # 에러발생: profile_file_url의 타입이 (예상되는 type인 str과) 다르다. (그래서 다른 방법으로 구현)
    profile_file_url: str | None

    # 만약 profile_file_url이 not None이라서 불러오는 경우, 
    # models.py에 있는 @property가 실행되면서, get_image_url 함수 실행됨

    class Config:
        orm_mode = True


# DONE: (user_id가 있을 때) 원하는 user의 정보 가져오기 찾기
@router.get("/{user_id:int}")
async def get_user(
    user_id: int,
    my_user_id: int = Depends(resolve_access_token),
) -> GetUserResponse:
    await validate_user_role(my_user_id, m.UserRoleEnum.Owner)  # Owner = 50

    user: m.User = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.User).where(m.User.id == user_id)
    )

    if user is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"There is no User whose user_id is {user_id}. Please try again."
        )

    return GetUserResponse.from_orm(user)


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
    message: str | None


# DONE: 유저에 대한 search (+ get_img_url)
@router.post("/search")
async def search_user(
    q: SearchUserRequest,
    my_user_id: int = Depends(resolve_access_token),
):
    await validate_user_role(my_user_id, m.UserRoleEnum.Owner)  # Owner = 50

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

    for user in users:
        if user.profile_file_key is not None:
            user.profile_file_url = get_image_url(user.profile_file_key)

    if user_cnt == 0:
        return SearchUserResponse(
            users=[GetUserResponse.from_orm(user) for user in users],
            count=user_cnt,
            message="Can't find a USER that meets the requirements. Please try again.",
        )
    else:
        return SearchUserResponse(
            users=[GetUserResponse.from_orm(user) for user in users],
            count=user_cnt,
        )


# DONE: 본인 프로필 불러오기
@router.get("/me")
async def get_my_profile(
    my_user_id: int = Depends(resolve_access_token),
):
    user: m.User | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.User).where(m.User.id == my_user_id)
    )

    if user is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"User not found."
        )
    
    if user.profile_file_key is not None:
        # TypeError: BaseEventLoop.run_in_executor() got an unexpected keyword argument 'Params'
        # user.profile_file_url = await get_image_url(user.profile_file_key)  # ERROR
        user.profile_file_url = get_image_url(user.profile_file_key)  # DONE
    
    return GetUserResponse.from_orm(user)

'''
    # if user.profile_file_key is not None:
    #     user.profile_file_url = await get_image_url(user.profile_file_key)


    # DONE: get_image_url()로 분리
    # if user.profile_file_key is not None:
    #     user.profile_file_url = AppCtx.current.s3.generate_presigned_url(
    #         "get_object",  # object를 가져오는 명령어 (변하지 않음))
    #         Params={
    #             "Bucket": "fastapi-practice",  # 서버에서 버킷 안 보냄(db의 테이블과 같은 의미)
    #             "Key": user.profile_file_key,  
    #         },
    #         ExpiresIn=60 * 60 * 24,  # a one day
    #     )
'''


class PostAttachmentResponse(BaseModel):
    bucket: str
    key: str


# DONE: 본인 프로필 '이미지만' 생성하기
@router.post("/profile_img")
async def post_user_profile_img(
    profile_file: UploadFile,
    my_user_id: int = Depends(resolve_access_token),
):
    """
    파일스토리지
    1. session
    2. resolve access token (user_id)
    3. blob client
    4. 사용자의 입력(file)
    """

    user: m.User | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.User).where(m.User.id == my_user_id)
    )

    if user is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    profile_file_key = await upload_profile_img(
        my_user_id,
        profile_file.filename,
        profile_file.file,  # file_object
    )
    
    user.profile_file_key = profile_file_key

    AppCtx.current.db.session.add(user)
    await AppCtx.current.db.session.commit()

    return PostAttachmentResponse(
        bucket=DEFAULT_BUCKET_NAME, 
        key=profile_file_key,
    )


class PutUserRequest(BaseModel):
    email: str


# DONE: 본인 프로필 업데이트 하기 (현재 email만)
# question: put으로 한번 더 UploadFile 하는게 의미 있는가? (의미 없음 그래서 안 함!)
@router.put("/me")
async def update_me(
    q: PutUserRequest,
    my_user_id: int = Depends(resolve_access_token),
):
    await validate_email_exist(q.email)

    user: m.User | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.User).where(m.User.id == my_user_id)
    )

    if user is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"User not found.",
        )
    
    user.email = q.email

    AppCtx.current.db.session.add(user)
    await AppCtx.current.db.session.commit()




class PostPasswordRequest(BaseModel):
    old_password: str
    new_password: str


# DONE
@router.put("/change-password")
async def change_password(
    q: PostPasswordRequest,
    my_user_id: int = Depends(resolve_access_token),
):
    user: m.User | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.User).where(m.User.id == my_user_id)
    )

    if not await validate_hashed_password(q.old_password, user.password):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Your password is incorrect."
        )

    user.password = await generate_hashed_password(q.new_password)

    AppCtx.current.db.session.add(user)
    await AppCtx.current.db.session.commit()



class PostRoleRequest(BaseModel):
    role: int
    user_id: int


# DONE
@router.put("/role")
async def change_user_role(
    q: PostRoleRequest,
    my_user_id: int = Depends(resolve_access_token),
):
    await validate_user_role(my_user_id, m.UserRoleEnum.Owner)

    user: m.User | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.User).where(m.User.id == q.user_id)
    )

    user.role = q.role

    AppCtx.current.db.session.add(user)
    await AppCtx.current.db.session.commit()


# DONE: 스스로 탈퇴하기 (권한은 all)
@router.delete("/")
async def delete_user(
    my_user_id: int = Depends(resolve_access_token),
):
    user: m.User | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.User).where(m.User.id == my_user_id)
    )

    await AppCtx.current.db.session.delete(user)
    await AppCtx.current.db.session.commit()


# DONE: (Owner 권한으로) 다른 유저 탈퇴시키기
@router.delete("/{user_id:int}")
async def delete_user(
    user_id: int,
    my_user_id: int = Depends(resolve_access_token),
):
    await validate_user_role(my_user_id, m.UserRoleEnum.Owner)

    user: m.User | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.User).where(m.User.id == user_id)
    )

    await AppCtx.current.db.session.delete(user)
    await AppCtx.current.db.session.commit()


