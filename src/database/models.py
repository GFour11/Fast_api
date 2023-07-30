from sqlalchemy import Column, String, Date, Integer
from sqlalchemy.ext.declarative import declarative_base

""" Ім'я
Прізвище
Електронна адреса
Номер телефону
День народження
Додаткові дані (необов'язково)"""

Base = declarative_base()

class Contact(Base):
    __tablename__ = 'Contacts'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable= False)
    surname = Column(String(100))
    email = Column(String(100))
    birthday = Column(Date)
    data = Column(String(), default= None)

