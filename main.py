from fastapi import FastAPI
from apis import API_ROUTERS

app = FastAPI()


for router in API_ROUTERS:
    app.include_router(router)