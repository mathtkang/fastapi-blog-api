import os
import re
import time

import dotenv
import jwt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.sql import expression as sql_exp
from starlette.status import HTTP_400_BAD_REQUEST

from app.database import models as m
from app.utils.auth import (
    generate_hashed_password,
    validate_email_exist,
    validate_hashed_password,
)
from app.utils.ctx import Context

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

router = APIRouter(prefix="/auth", tags=["auth"])


PASSWORD_REGEX = (
    r"^("
    r"(?=.*{letters})(?=.*{digits})(?=.*{specials})"
    r"|(?=.*{letters})(?=.*{digits})"
    r"|(?=.*{letters})(?=.*{specials})"
    r"|(?=.*{digits})(?=.*{specials})"
    r").{{8,}}$"
).format(
    letters="[a-zA-Z]",
    digits="[0-9]",
    specials="""[~`!@#$%^&*()=+[{\]}\\|;:'",<.>/?_-]""",
)


class AuthRequest(BaseModel):
    email: str
    password: str = Field(regex=PASSWORD_REGEX)


@router.post("/signup")
async def signup(q: AuthRequest):
    """
    This is the endpoint for the login page.
    """

    await validate_email_exist(q.email)

    user = m.User(email=q.email, password=await generate_hashed_password(q.password))

    Context.current.db.session.add(user)
    await Context.current.db.session.commit()


class LoginResponse(BaseModel):
    access_token: str


@router.post("/login", response_model=LoginResponse)
async def login(q: AuthRequest):
    user: m.User | None = await Context.current.db.session.scalar(
        sql_exp.select(m.User).where(m.User.email == q.email)
    )

    if user is None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="user not found")

    if not await validate_hashed_password(q.password, user.password):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Your password is incorrect."
        )

    access_token = jwt.encode(
        payload={
            "_id": user.id,
            "iat": int(time.time()),
            "iss": "fastapi-practice",
            "exp": int(time.time()) + 60 * 60 * 24,
        },
        key=os.environ["SECRET_KEY"],
    )

    return LoginResponse(access_token=access_token)


# @router.post("/logout")
# def logout():
#     '''
#     You cannot make a logout router. Because session information is not stored,
#     '''
