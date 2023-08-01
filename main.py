from fastapi import FastAPI, status, Request
from starlette.responses import JSONResponse

from src.routers.routers import router, utils

app = FastAPI()

app.include_router(router)
app.include_router(utils)

@app.exception_handler(Exception)
def unexpected_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An unexpected error occurred"})

