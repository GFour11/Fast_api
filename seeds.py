from faker import Faker
from src.database.db import SESSION
from src.database.models import Contact

fake = Faker('uk-UA')

def fill_db():
    info = 'Some info'
    flag = True
    session = SESSION()
    for db_new_object in range(5):
        name = fake.name().split(' ')
        if flag:
            obj = Contact(name = name[0], surname =name[1], email = fake.email(), birthday = fake.date_of_birth(), data = info)
            flag = False
        else:
            obj = Contact(name=name[0], surname=name[1], email=fake.email(), birthday=fake.date_of_birth())
            flag = True
        session.add(obj)
        session.commit()









