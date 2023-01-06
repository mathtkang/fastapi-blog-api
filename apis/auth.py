from fastapi import Depends, APIRouter, HTTPException
from db.db import get_session
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db import models as m
from sqlalchemy.sql import expression as sql_exp
from utils.auth import generate_hashed_password, validate_hashed_password
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST
import jwt, time


router = APIRouter(prefix="/auth", tags=["auth"])


class AuthSignupRequest(BaseModel):
    email: str
    password: str


@router.post("/signup")
def signup(q: AuthSignupRequest, session: Session = Depends(get_session)):
    """
    This is the endpoint for the login page.
    """
    if session.scalar(sql_exp.exists().where(m.User.email == q.email).select()):
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail="Email already exists"
        )

    user = m.User(email=q.email, password=generate_hashed_password(q.password))

    session.add(user)
    session.commit()


class LoginResponse(BaseModel):
    access_token: str


@router.post("/login", response_model=LoginResponse)
def login(q: AuthSignupRequest, session: Session = Depends(get_session)):
    user: m.User | None = session.execute(
        sql_exp.select(m.User).where(m.User.email == q.email)
    ).scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="user not found")

    if not validate_hashed_password(q.password, user.password):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="password is wrong"
        )

    access_token = jwt.encode(
        payload={
            "_id": user.id,
            "iat": int(time.time()),
            "iss": "fastapi-practice",
            "exp": int(time.time()) + 60 * 60 * 24,  # 알아서 검증
        },
        key="secret",
    )

    return LoginResponse(access_token=access_token)


# @router.post("/logout")
# def logout():
#     '''
#     You cannot make a logout router. Because session information is not stored,
#     '''
