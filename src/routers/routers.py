from datetime import date
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repositories.operations import get_one_contact, del_contact
import src.repositories.operations as src
from src.schemas import ContactResponse

router = APIRouter(prefix='/contacts', tags=['contacts'])
utils = APIRouter(prefix='/utils', tags=['utils'])

@router.get('/get_contatact', response_model=ContactResponse)
async def get_contact(contact_id, db: Session = Depends(get_db)):
    result = await get_one_contact(contact_id, db)
    return result

@router.get('/get_all_contatact')
async def get_all_contact(db: Session = Depends(get_db)):
    result = await src.get_all_contacts(db)
    return result


@router.put('/update_contatact')
async def update_contact(contact_id, body : ContactResponse, db: Session = Depends(get_db)):
    result = await src.update_contact(contact_id, body, db)
    return result

@router.delete('/delete_contact')
async def delete_contact(contact_id, db: Session = Depends(get_db)):
    await del_contact(contact_id, db)
    return 'Delited'

@router.post('/new_contatact', response_model=ContactResponse)
async def create_contact(body : ContactResponse, db: Session = Depends(get_db)):
    result = await src.create_contact(body, db)
    return result

@utils.get('/upcoming_birthday')
async def upcoming_birthday(db: Session = Depends(get_db)):
    result = await src.upcoming_birthday(db)
    return result
@utils.get('/search')
async def search(param, db: Session = Depends(get_db)):
    result = await src.search(param, db)
    return result