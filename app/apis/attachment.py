from fastapi import Depends, APIRouter, HTTPException, UploadFile
from app.utils.auth import resolve_access_token
from sqlalchemy.ext.asyncio import AsyncSession as Session
from pydantic import BaseModel
from app.database import models as m
from sqlalchemy.sql import expression as sql_exp
from app.utils.blob import upload_image
from starlette.status import HTTP_403_FORBIDDEN
from mypy_boto3_s3.client import S3Client
from app.utils.ctx import AppCtx


router = APIRouter(prefix="/attachment", tags=["attachment"])


class PostAttachmentResponse(BaseModel):
    bucket: str
    key: str


@router.post("")
async def post_attachment(
    file: UploadFile,
    user_id: int = Depends(resolve_access_token),
):
    """
    파일스토리지
    1. session
    2. resolve access token (user_id)
    3. blob client
    4. 사용자의 입력(file)
    """
    user: m.User | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.User).where(m.User.id == user_id)
    )

    if user is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="User not found",
        )

    attachment_file_key = await upload_image(
        user_id, 
        file.filee, 
        file.file
    )

    return PostAttachmentResponse(bucket="fastapi-practice", key=attachment_file_key)


# class PutUserRequest(BaseModel):
#     profile_file_key: str | None
#     # 예) 기본프로필로 변경

# @router.post("/me")
# async def create_me(
#     q: PutUserRequest,
#     user_id: int = Depends(resolve_access_token),
# ):
#     user: m.User | None = await AppCtx.current.db.session.scalar(
#         sql_exp.select(m.User).where(m.User.id == user_id)
#     )

#     if user is None:
#         raise HTTPException(
#             status_code=HTTP_403_FORBIDDEN,
#             detail="User not found",
#         )

#     user.profile_file_key = q.profile_file_key

#     AppCtx.current.db.session.add(user)
#     await AppCtx.current.db.session.commit()




# URL: 제한시간, 해당 리소스에만 접근 가능

# 1. upload file by this endpoint
# 2. get the attachment file key
# 3. upload attachment key to post or user
# 4. get attachment file url by user get endpoint or post get endpoint


'''
하나의 엔드포인트에 대해서?
1. Client가 Server에게 Request를 날렸다.

final. Client가 Server로부터 Response를 받았다.
'''
