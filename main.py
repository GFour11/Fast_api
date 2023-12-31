import os

from fastapi import FastAPI, status, Request
from fastapi_limiter import FastAPILimiter
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from dotenv import load_dotenv


from src.routers.routers import router, utils, users

app = FastAPI()
load_dotenv()

origins = [
    "http://localhost:8000"
    ]

app.include_router(router)
app.include_router(utils)
app.include_router(users)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.exception_handler(Exception)
def unexpected_exception_handler(request: Request, exc: Exception):
    """Exception decorator"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An unexpected error occurred"})


@app.on_event("startup")
async def startup():
    """Redis plus FastapiLimiter"""
    r = await redis.Redis(host=os.environ.get('REDIS_HOST'),
                          port=os.environ.get('REDIS_PORT'), password=os.environ.get('REDIS_PASSWORD'),
                          db=0, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)