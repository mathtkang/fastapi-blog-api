from fastapi import FastAPI
from controllers import API_ROUTERS
from settings import AppSettings


def create_app(app_settings: AppSettings) -> FastAPI:
    app = FastAPI()
    # app_settings = app.settings  # question

    for api_router in API_ROUTERS:
        app.include_router(api_router)

    return app


app = create_app(AppSettings())