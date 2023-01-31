from fastapi import FastAPI
import uvicorn
from app.settings import AppSettings
from app import create_app


app_settings = AppSettings()


app = create_app(app_settings)

if __name__ == "__main__":
    uvicorn.run(app)
