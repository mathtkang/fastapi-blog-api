from httpx import AsyncClient
from test.constants import (
    DEFAULT_USER_EMAIL, 
    DEFAULT_USER_PASSWORD, 
    DEFAULT_OWNER_EMAIL,
    DEFAULT_OWNER_PASSWORD,
)
from app.utils.ctx import AppCtx
from sqlalchemy.sql import expression as sql_exp
from app.database import models as m


async def create_user(app_client: AsyncClient) -> None:
    response = await app_client.post(
        '/auth/signup',
        json={
            "email": DEFAULT_USER_EMAIL,
            "password": DEFAULT_USER_PASSWORD,
        },
    )
    return response


async def create_owner(app_client: AsyncClient) -> None:
    response = await app_client.post(
        '/auth/signup',
        json={
            "email": DEFAULT_OWNER_EMAIL,
            "password": DEFAULT_OWNER_PASSWORD,
        },
    )

    user = await AppCtx.current.db.session.scalar(
        sql_exp.select(m.User).where(m.User.email == DEFAULT_OWNER_EMAIL)
    )
    user.role = m.UserRoleEnum.Owner

    AppCtx.current.db.session.add(user)
    await AppCtx.current.db.session.commit()

    return response