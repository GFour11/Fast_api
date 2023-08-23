from fastapi import status, HTTPException
from datetime import date, timedelta
from sqlalchemy import or_
from src.database.models import Contact, User
from sqlalchemy.orm import Session

from src.repositories.auth import Hash, get_user_by_email

hash_handler = Hash()
async def get_all_contacts(user: User,db: Session):
    """
    Get a list of all contacts for current user.

    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: List[Contact objects]
    """
    result = db.query(Contact).filter_by(user = user.id).all()
    return result

async def create_contact(body, user: User, db: Session):
    """
    Create a new contact for current user.

    :param body: data about new contact.
    :type body: JSON
    :param user: The user to retrieve contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: new contact.
    :rtype: Contact object
    """
    contact = Contact(name = body.name, surname = body.surname, email = body.email, birthday = body.birthday, data = body.data, user = user.id)
    db.add(contact)
    db.commit()
    return contact

async def get_one_contact(name, user: User, db: Session):
    """
    Get a one contact for current user.

    :param name: name of contact.
    :type name: string
    :param user: The user to retrieve Contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: contact.
    :rtype: Contact object
    """
    return db.query(Contact).filter_by(name = name, user = user.id).first()

async def update_contact(name, body, user: User, db: Session):
    """
    Update one contact for current user.

    :param name: name of contact.
    :type name: string
    :param body: data for updating contact
    :param body: JSON
    :param user: The user to retrieve Contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: contact or None if contact is not exist.
    :rtype: Contact object | None
    """

    contact = db.query(Contact).filter_by(name = name, user = user.id).first()
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


async def del_contact(name, user: User, db: Session):
    """
      Delite one contact for current user.

      :param name: name of contact.
      :type name: string
      :param user: The user to retrieve Contacts for.
      :type user: User
      :param db: The database session.
      :type db: Session
      :return: None.
      """

    contact = db.query(Contact).filter_by(name = name, user = user.id).first()
    if contact:
        db.delete(contact)
        db.commit()
    else:
        return None


async def upcoming_birthday(user: User,db: Session):
    """
      Find all contacts for current user, wich have a birthday on this week.

      :param user: The user to retrieve Contacts for.
      :type user: User
      :param db: The database session.
      :type db: Session
      :return: contacts.
      :rtype: List[Contact objects]
      """

    result_list =[]
    contacts = db.query(Contact).filter_by(user=user.id).order_by('birthday').all()
    current_date = date.today()
    end_of_week = current_date + timedelta(days=6 - current_date.weekday())
    for contact in contacts:
        if contact.birthday.month == current_date.month and contact.birthday.day >= current_date.day and contact.birthday <= end_of_week:
            result_list.append(contact)
    return result_list


async def search(param, user: User, db: Session):
    """
      Find a contact for current user, with specify parameter(name, surname, email).

      :param param: parameter for search.
      :type param: string
      :param user: The user to retrieve Contacts for.
      :type user: User
      :param db: The database session.
      :type db: Session
      :return: contact.
      :rtype: Contact object
      """
    contacts = db.query(Contact).filter_by(user = user.id).filter(or_(Contact.name.ilike(f'%{param}%'),(Contact.surname.ilike(f'%{param}%')),
                                            (Contact.email.ilike(f'%{param}%')))).all()
    return contacts

async def signup(body, db: Session):
    """Signup function

    :param body: json with email and password.
    :type body: JSON
    :param db: The database session.
    :type db: Session
    :return: new_user.
    :rtype: User
    """
    is_exist = db.query(User).filter_by(email = body.email).first()
    if is_exist:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is all ready exist")
    new_user = User(email = body.email, password = hash_handler.get_password_hash(body.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

async def confirmed_email( email, db: Session):
    """User confirmed his email

    :param email: user email.
    :type email: string
    :param db: The database session.
    :type db: Session
    :return: None.
    """

    user = db.query(User).filter_by(email=email).first()
    user.confirmed = True
    db.commit()
    return None

async def update_avatar(email, url: str, db: Session) -> User:
    """
    Change or update avatar for user.

    :param email: user email.
    :type email: string
    :param url: link to user new avatar.
    :type url: string
    :param db: The database session.
    :type db: Session
    :return: user.
    :rtype: User objact
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user