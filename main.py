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

# @router.get('/get_contatact', response_model=ContactResponse)
# async def get_contact(contact_id, db: Session = Depends(get_db)):
#     result = await get_one_contact(contact_id, db)
#     if not result:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
#     return result