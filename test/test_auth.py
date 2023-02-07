from fastapi.testclient import TestClient
import pytest_asyncio
import pytest
import json
from httpx import AsyncClient
from app.apis.board import router
from app.settings import AppSettings
from test.helper import with_app_ctx, ensure_fresh_env

# Test the user registration endpoint - POST /api/v1/auth/register
def test_signup(app_client: AsyncClient):
    pass


# Test the user login endpoint - POST /api/v1/auth/login
def test_login(client: TestClient):
    pass