# from . import app
from fastapi import FastAPI
from .settings import AppSettings
from .apis import API_ROUTERS




def create_app(app_settings: AppSettings) -> FastAPI:
    # 앱 함수 실행
    app = FastAPI()

    # 라우터 정의
    for api_router in API_ROUTERS:
        app.include_router(api_router)

    return app