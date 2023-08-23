import os
from _datetime import datetime
from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from src.database.db import get_db
from src.database.models import User


class Hash:
    """ User authentication class"""

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Verify if a plain password matches the hashed password.

        :param plain_password: password entered by the user.
        :type plain_password: str
        :param hashed_password: user password transformed in hash.
        :type hashed_password: str
        :return: True or False
        :rtype: Bool
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Transformed password in hash.

        :param password: user password.
        :type password: str
        :return: user password transformed in hash.
        :rtype: str
        """
        return self.pwd_context.hash(password)

load_dotenv()
SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = os.environ.get('ALGORITHM')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/utils/login")


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Search and return user object from database.

    :param email: user email.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: User objects | None
    """
    return db.query(User).filter_by(email = email).first()

async def create_access_token(data: dict, expires_delta: Optional[float] = None):
    """
    Create access token for user.

    :param data: data about user current access parameters.
    :type data: dict
    :param expires_delta: Expiration time in seconds. Default is None.
    :type expires_delta: float
    :return: user access token
    :rtype: str
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
    encoded_access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_access_token



async def create_refresh_token(data: dict, expires_delta: Optional[float] = None):
    """
    Create refresh token for user.

    :param data: data about user current access parameters.
    :type data: dict
    :param expires_delta: Expiration time in seconds. Default is None.
    :type expires_delta: float
    :return: user refresh token
    :rtype: str
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
    encoded_refresh_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_refresh_token


async def get_email_form_refresh_token(refresh_token: str):
    """
    Get user email from payload "scope" in refresh token.

    :param refresh_token: user refresh token.
    :type refresh_token: str
    :return: user email.
    :rtype: str
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload['scope'] == 'refresh_token':
            email = payload['sub']
            return email
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    We get user email from payload "scope", then try to find user in database.

    :param token: user access token, wich depends on OAuth2Sheme.
    :type token: str
    :param db: The database session.
    :type db: Session
    :return: User objects
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload['scope'] == 'access_token':
            email = payload["sub"]
            if email is None:
                raise credentials_exception
        else:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    user: User = db.query(User).filter_by(email = email).first()
    if user is None:
        raise credentials_exception
    return user


async def decode_refresh_token(self, refresh_token: str):
    """
    Decoding refresh token.

    :param refresh_token: user refresh token.
    :type refresh_token: str
    :return: user email
    """
    try:
        payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        if payload['scope'] == 'refresh_token':
            email = payload['sub']
            return email
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Create a new refresh token for user.

    :param user: current user.
    :type user: User object
    :param token: user refresh token.
    :type token: str
    :param db: The database session.
    :type db: Session
    :return: None
    """
    user.refresh_token = token
    db.commit()

async def create_email_token(data: dict):
    """
    Create email token for user.

    :param data: data about user current access parameters.
    :type data: dict
    :return: user email token
    :rtype: str
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(token)
    return token


async def get_email_from_token(token: str):
    """
    Get user email from payload "sub" in token.

    :param token: user refresh token.
    :type token: str
    :return: user email.
    :rtype: str
    """
    try:
      payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
      print(payload)
      email = payload["sub"]
      print(email)
      return email
    except JWTError as e:
      print(e)
      raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                          detail="Invalid token for email verification")