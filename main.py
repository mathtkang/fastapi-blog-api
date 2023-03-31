import uvicorn
from fastapi import FastAPI
from app import create_app
from app.settings import AppSettings


app_settings = AppSettings()


app = create_app(app_settings)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5468)
