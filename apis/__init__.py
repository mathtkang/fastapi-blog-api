from .board import router as board_router
from .auth import router as auth_router

API_ROUTERS = [board_router, auth_router]
