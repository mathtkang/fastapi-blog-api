from .auth import router as auth_router
from .user import router as user_router
from .board import router as board_router
from .post import router as post_router
from .comment import router as comment_router
from .hashtag import router as hashtag_router
from .attachment import router as attachment_router

API_ROUTERS = [
    auth_router,
    user_router,
    board_router,
    post_router,
    comment_router,
    hashtag_router,
    attachment_router,
]
