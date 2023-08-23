from sqlalchemy import Column, String, Date, Integer, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Contact(Base):

    """Contact object model"""

    __tablename__ = 'Contacts'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable= False)
    surname = Column(String(100))
    email = Column(String(100))
    birthday = Column(Date)
    data = Column(String(), default= None)
    user = Column(ForeignKey("Users.id", ondelete="CASCADE"), nullable=True, default=None)

class User(Base):

    """User object model"""

    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    email = Column(String(50), nullable= False, unique= True)
    password = Column(String(), nullable= False)
    access_token = Column(String(300), default=None)
    refresh_token = Column(String(300), default=None)
    confirmed = Column(Boolean(), default=False)
    avatar = Column(String(255), nullable=True)

    def __str__(self):
        return self.email