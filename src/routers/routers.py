from fastapi import APIRouter, Depends,  HTTPException, status, BackgroundTasks, Request
from fastapi.security import  HTTPBearer, OAuth2PasswordRequestForm
from fastapi_mail import MessageSchema, MessageType, FastMail
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repositories import auth as auth
from src.repositories.auth import get_user_by_email
from src.repositories.email import EmailSchema, conf, send_email
from src.repositories.operations import get_one_contact, del_contact, confirmed_email
import src.repositories.operations as src
from src.schemas import ContactResponse, UserModel, TokenModel, RequestEmail


router = APIRouter(prefix='/contacts', tags=['contacts'])
utils = APIRouter(prefix='/utils', tags=['utils'])
security = HTTPBearer()
@router.get('/get_contatact', response_model=ContactResponse)
async def get_contact(name, current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    result = await get_one_contact(name, current_user, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return result


@router.get('/get_all_contatact')
async def get_all_contact(current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    result = await src.get_all_contacts(current_user,db)
    return result


@router.put('/update_contatact', status_code=status.HTTP_201_CREATED)
async def update_contact(name, body : ContactResponse, current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    result = await src.update_contact(name, body, current_user, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return result

@router.delete('/delete_contact')
async def delete_contact(name,current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    result = await del_contact(name, current_user, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return 'Delited'

@router.post('/new_contatact', response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body : ContactResponse, current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    result = await src.create_contact(body,current_user, db)
    return result

@utils.get('/upcoming_birthday')
async def upcoming_birthday(current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    result = await src.upcoming_birthday(current_user, db)
    return result
@utils.get('/search')
async def search(param, current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    result = await src.search(param, current_user, db)
    return result

@utils.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(body : UserModel ,background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    new_user = await src.signup(body, db)
    background_tasks.add_task(send_email, body.email, request.base_url)
    return 'Check your email'
@utils.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not src.hash_handler.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    access_token = await auth.create_access_token(data={"sub": user.email})
    refresh_token = await auth.create_refresh_token(data={"sub": user.email})
    user.access_token = access_token
    db.commit()
    await auth.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@utils.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = await auth.get_email_from_token(token)
    user = await auth.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await confirmed_email(email, db)
    return {"message": "Email confirmed"}

@utils.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    user = await auth.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}