from fastapi import FastAPI, status, Request
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.routers.routers import router, utils, users

app = FastAPI()

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
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An unexpected error occurred"})

@app.on_event("startup")
async def startup():
    r = await redis.Redis(host='localhost', port=6379, db=0, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)