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
    data: str | None

    class Config:
        orm_mode = True
