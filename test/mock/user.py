from test.constants import (
    DEFAULT_OWNER_EMAIL,
    DEFAULT_OWNER_PASSWORD,
    DEFAULT_USER_EMAIL,
    DEFAULT_USER_PASSWORD,
)

from httpx import AsyncClient
from sqlalchemy.sql import expression as sql_exp

from app.database import models as m
from app.utils.ctx import Context


async def create_user(app_client: AsyncClient) -> None:
    response = await app_client.post(
        "/auth/signup",
        json={
            "email": DEFAULT_USER_EMAIL,
            "password": DEFAULT_USER_PASSWORD,
        },
    )
    return response


async def create_owner(app_client: AsyncClient) -> None:
    response = await app_client.post(
        "/auth/signup",
        json={
            "email": DEFAULT_OWNER_EMAIL,
            "password": DEFAULT_OWNER_PASSWORD,
        },
    )

    user = await Context.current.db.session.scalar(
        sql_exp.select(m.User).where(m.User.email == DEFAULT_OWNER_EMAIL)
    )
    user.role = m.UserRoleEnum.Owner

    Context.current.db.session.add(user)
    await Context.current.db.session.commit()

    return response
