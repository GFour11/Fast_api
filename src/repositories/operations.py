from fastapi import status
from datetime import date, timedelta
from sqlalchemy import or_
from src.database.models import Contact
from sqlalchemy.orm import Session


async def get_all_contacts(db: Session):
    result = db.query(Contact).all()
    return result

async def create_contact(body, db: Session):
    contact = Contact(name = body.name, surname = body.surname, email = body.email, birthday = body.birthday, data = body.data)
    db.add(contact)
    db.commit()
    return contact

async def get_one_contact(id, db: Session):
    return db.query(Contact).filter_by(id = id).first()

async def update_contact(id, body, db: Session):
    contact = db.query(Contact).filter_by(id = id).first()
    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.email = body.email
        contact.birthday = body.birthday
        contact.data = body.data
        db.commit()
        db.refresh(contact)
        return contact
    else:
        return None


async def del_contact(id, db: Session):
    contact = db.query(Contact).filter_by(id = id).first()
    if contact:
        db.delete(contact)
        db.commit()
    else:
        return None


async def upcoming_birthday(db: Session):
    result_list =[]
    contacts = db.query(Contact).order_by('birthday').all()
    current_date = date.today()
    end_of_week = current_date + timedelta(days=6 - current_date.weekday())
    for contact in contacts:
        if contact.birthday.month == current_date.month and contact.birthday.day >= current_date.day and contact.birthday <= end_of_week:
            result_list.append(contact)
    return result_list


async def search(param, db: Session):
    contacts = db.query(Contact).filter(or_(Contact.name.ilike(f'%{param}%'),(Contact.surname.ilike(f'%{param}%')),
                                            (Contact.email.ilike(f'%{param}%')))).all()
    return contacts

