from .attachment import router as attachment_router
from .auth import router as auth_router
from .board import router as board_router
from .comment import router as comment_router
from .hashtag import router as hashtag_router
from .post import router as post_router
from .user import router as user_router

__all__ = ["ALL_ROUTERS"]

API_ROUTERS = [
    attachment_router,
    auth_router,
    board_router,
    comment_router,
    hashtag_router,
    post_router,
    user_router,
]