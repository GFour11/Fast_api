from fastapi import FastAPI

from src.routers.routers import router, utils

app = FastAPI()

app.include_router(router)
app.include_router(utils)

