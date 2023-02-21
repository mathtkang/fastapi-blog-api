# from fastapi import Depends, APIRouter, HTTPException, UploadFile
# from pydantic import BaseModel
# from sqlalchemy.ext.asyncio import AsyncSession as Session
# from sqlalchemy.sql import expression as sql_exp
# from starlette.status import HTTP_404_NOT_FOUND
# from mypy_boto3_s3.client import S3Client

# from app.database import models as m
# from app.utils.auth import resolve_access_token, validate_user_role
# from app.utils.blob import upload_image
# from app.utils.ctx import AppCtx


# router = APIRouter(prefix="/attachment", tags=["attachment"])




# # 프로필 '파일만' 삭제
# # @router.delete("")
# # async def delete_attachment():





# # URL: 제한시간, 해당 리소스에만 접근 가능

# # 1. upload file by this endpoint
# # 2. get the attachment file key
# # 3. upload attachment key to post or user
# # 4. get attachment file url by user get endpoint or post get endpoint