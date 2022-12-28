from .board import router as board_router
from .post import router as post_router
from .comment import router as comment_router
from .auth import router as auth_router

API_ROUTERS = [
    board_router, 
    auth_router, 
    post_router, 
    comment_router
]
