from datetime import date
from pydantic import BaseModel, Field

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
    email : str
    password: str

class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"