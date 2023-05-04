import uvicorn
from fastapi import FastAPI
from app import create_app
from app.settings import AppSettings


app_settings = AppSettings()


app = create_app(app_settings)

if __name__ == "__main__":
    uvicorn.run(app, host="54.180.152.156", port=8000)
