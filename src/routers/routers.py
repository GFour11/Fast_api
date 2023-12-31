import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends,  HTTPException, status, BackgroundTasks, Request, UploadFile, File
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter


from src.database.db import get_db
from src.database.models import User
from src.repositories import auth as auth
from src.repositories.auth import get_user_by_email
from src.repositories.email import send_email
from src.repositories.operations import get_one_contact, del_contact, confirmed_email
import src.repositories.operations as src
from src.schemas import ContactResponse, UserModel, TokenModel, RequestEmail, UserDb


router = APIRouter(prefix='/contacts', tags=['contacts'])
utils = APIRouter(prefix='/utils', tags=['utils'])
users = APIRouter(prefix='/users', tags=['users'])
security = HTTPBearer()


@router.get('/get_contatact', response_model=ContactResponse)
async def get_contact(name, current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Find one contact for current user with parameter NAME.

    :param name: contact name.
    :type name: str
    :param current_user: user object.
    :type current_user:  class User object
    :param db: The database session.
    :type db: Session
    :return: Contact with new data.
    :rtype: Contact object
    """
    result = await get_one_contact(name, current_user, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return result


@router.get('/get_all_contatact', dependencies=[Depends(RateLimiter(times=1, seconds=5))])
async def get_all_contact(current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Get all contacts for current user from db

    :param current_user: user object.
    :type current_user:  class User object
    :param db: The database session.
    :type db: Session
    :return: List[Contacts objects]
    """
    result = await src.get_all_contacts(current_user,db)
    return result


@router.put('/update_contatact', status_code=status.HTTP_201_CREATED,  dependencies=[Depends(RateLimiter(times=1, seconds=5))])
async def update_contact(name, body : ContactResponse, current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Update existing contact with new information.

    :param name: contact name.
    :type name: str
    :param body: contact name, surname, birthday, data.
    :type body: JSON
    :param current_user: user object.
    :type current_user:  class User object
    :param db: The database session.
    :type db: Session
    :return: Contact with new data.
    :rtype: Contact object
    """
    result = await src.update_contact(name, body, current_user, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return result

@router.delete('/delete_contact')
async def delete_contact(name,current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Create a new contact.

    :param name: contact name.
    :type name: str
    :param current_user: user object.
    :type current_user:  class User object
    :param db: The database session.
    :type db: Session
    :return: (str) message 'Delited'.
    """
    result = await del_contact(name, current_user, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return 'Delited'

@router.post('/new_contatact', response_model=ContactResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def create_contact(body: ContactResponse, current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Create a new contact.

    :param body: contact name, surname, birthday, data.
    :type body: JSON
    :param current_user: user object.
    :type current_user:  class User object
    :param db: The database session.
    :type db: Session
    :return: new contact.
    """
    result = await src.create_contact(body,current_user, db)
    return result


@utils.get('/upcoming_birthday')
async def upcoming_birthday(current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Find contacts, who have a birthday on this week.

    :param current_user: user object.
    :type current_user:  class User object
    :param db: The database session.
    :type db: Session
    :return: List[Contacts objects]
    """
    result = await src.upcoming_birthday(current_user, db)
    return result
@utils.get('/search')
async def search(param, current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """
    Find any contact with specific parameter.

    :param param: str. Word for find info.
    :param current_user: user object.
    :type current_user:  class User object
    :param db: The database session.
    :type db: Session
    :return: List[User objects]
    """
    result = await src.search(param, current_user, db)
    return result

@utils.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(body : UserModel ,background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Sign up.

    :param body: user email, password.
    :type body: json
    :param background_tasks: fastapi BackgroundTasks.
    :type background_tasks: function
    :param request: fastapi Request.
    :type request: Request object
    :param db: The database session.
    :type db: Session
    :return: str
    """
    await src.signup(body, db)
    background_tasks.add_task(send_email, body.email, request.base_url)
    return 'Check your email'
@utils.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """User login function.
    :param body: user data depends on fastapi security OAuth2PasswordRequestForm.
    :type body:OAuth2PasswordRequestForm object
    :param db: The database session.
    :type db: Session
    :return: access token, refresh token.
    """
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
async def _confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirm email for current user.

    :param token: user token.
    :type token: str
    :param db: The database session.
    :type db: Session
    :return: str
    """
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
    """
    Send email to user, to confirmed his registration.

    :param body: user email.
    :type body: str
    :param background_tasks: fastapi BackgroundTasks.
    :type background_tasks: function
    :param request: fastapi Request.
    :type request: Request object
    :param db: The database session.
    :type db: Session
    :return: str
    """
    user = await auth.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}

@users.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth.get_current_user),
                             db: Session = Depends(get_db)):
    """
    Update user avatar.

    :param file: new avatar file. Depends on fastapi UploadFile.
    :type file: file path
    :param current_user: user object.
    :type current_user:  class User object
    :param db: The database session.
    :type db: Session
    :return: User object
    """
    cloudinary.config(
        cloud_name="dsjusqa4p",
        api_key="599877185773136",
        api_secret="VFeBRMltUi1d8Jz_aCwOGLF4b8k",
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'ContactApp/{current_user.email}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'ContactApp/{current_user.email}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await src.update_avatar(current_user.email, src_url, db)
    return user

@users.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth.get_current_user)):
    ''' User profile.

    :param current_user: user object.
    :type current_user:  class User object
    :return: User object
    '''
    return current_user