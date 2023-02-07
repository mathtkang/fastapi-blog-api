from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession as Session
import re
from pydantic import BaseModel, Field
from sqlalchemy.sql import expression as sql_exp
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST
import jwt, time
from app.database import models as m
from app.utils.auth import generate_hashed_password, validate_hashed_password
from app.utils.ctx import AppCtx
import dotenv
import os


dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)


router = APIRouter(prefix="/auth", tags=["auth"])


PASSWORD_REGEX = (
    r'^('
    r'(?=.*{letters})(?=.*{digits})(?=.*{specials})'
    r'|(?=.*{letters})(?=.*{digits})'
    r'|(?=.*{letters})(?=.*{specials})'
    r'|(?=.*{digits})(?=.*{specials})'
    r').{{8,}}$'
).format(
    letters='[a-zA-Z]',
    digits='[0-9]',
    specials='''[~`!@#$%^&*()=+[{\]}\\|;:'",<.>/?_-]''',
)


class AuthSignupRequest(BaseModel):
    email: str
    password: str = Field(regex=PASSWORD_REGEX)


@router.post("/signup")
async def signup(q: AuthSignupRequest):
    """
    This is the endpoint for the login page.
    """
    is_email_exist = await AppCtx.current.db.session.scalar(
        sql_exp.exists().where(m.User.email == q.email).select()
    )
    if is_email_exist:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail="Email already exists"
        )

    user = m.User(email=q.email, password=generate_hashed_password(q.password))

    AppCtx.current.db.session.add(user)
    await AppCtx.current.db.session.commit()


class LoginResponse(BaseModel):
    access_token: str


@router.post("/login", response_model=LoginResponse)
async def login(q: AuthSignupRequest):
    user: m.User | None = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.User).where(m.User.email == q.email)
    )

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
            "exp": int(time.time()) + 60 * 60 * 24,
        },
        key=os.environ["SECRET_KEY"],  # .env
    )

    return LoginResponse(access_token=access_token)


# @router.post("/logout")
# def logout():
#     '''
#     You cannot make a logout router. Because session information is not stored,
#     '''
