from httpx import AsyncClient
from test.constants import DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD


async def create_user(app_client: AsyncClient) -> None:
    resp = await app_client.post(
        '/auth/signup',
        json={
            "email": DEFAULT_USER_EMAIL,
            "password": DEFAULT_USER_PASSWORD,
        },
    )

    assert resp.status_code == 200