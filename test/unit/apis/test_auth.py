from fastapi.testclient import TestClient

import pytest_asyncio
import pytest
import json
from httpx import AsyncClient
from app.apis.board import router
from app.settings import AppSettings
from ...helper import with_app_ctx, ensure_fresh_env

# Test the user registration endpoint - POST /auth/signup
def test_signup(app_client: AsyncClient):    
    pass
    


# Test the user login endpoint - POST /auth/login
def test_login(client: TestClient):
    pass