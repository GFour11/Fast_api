from datetime import date
from pydantic import BaseModel, Field, EmailStr


class ContactModel(BaseModel):
    name : str = Field(max_length=100)
    surname : str = Field(max_length=100)
    email : str = Field(max_length=100)
    birthday : date
    data : str = Field(default=None)

class ContactResponse(ContactModel):
    name: str
    surname: str
    email: str
    birthday: date
    data: str

    class Config:
        from_attributes = True

class UserModel(BaseModel):
    email: str
    password: str

class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RequestEmail(BaseModel):
    email : EmailStr

class UserDb(BaseModel):
    id: int
    email: str
    avatar: str

    class Config:
        orm_mode = True