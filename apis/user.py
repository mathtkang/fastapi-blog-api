from fastapi import Depends, APIRouter, HTTPException
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
):
    users: list[m.User] = session.execute(sql_exp.select(m.User)).scalars().all()

    return [GetUserInformationResponse.from_orm(user) for user in users]



@router.get("/me")
def get_my_information(
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    validate_user_role(user_id, m.UserRoleEnum.Admin, session)

    user: m.User | None = session.execute(
        sql_exp.select(m.User).where(m.User.id == user_id)
    ).scalar_one_or_none()

    return JSONResponse({
        "email": user.email,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "role": user.role
    })
    


@router.put("/me")
def update_my_profile():
    pass



class PostRoleRequest(BaseModel):
    role: int

@router.put("/role")
def change_user_role(
    q: PostRoleRequest,
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    validate_user_role(user_id, m.UserRoleEnum.Owner, session)

    user: m.User | None = session.execute(
        sql_exp.select(m.User).where(m.User.id == user_id)
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

    if user.password != q.old_password:
        raise HTTPException(

        )

    user.password = q.new_password

    session.add(user)
    session.commit()



@router.get("/posts")
def get_my_post():
    pass




@router.get("/likes")
def get_liked_post():
    pass