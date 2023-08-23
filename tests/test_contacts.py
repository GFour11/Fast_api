import unittest
from datetime import date
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.repositories.operations import get_all_contacts, create_contact, get_one_contact, del_contact, update_contact
from src.schemas import ContactModel


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=30)
        self.contact = Contact(name = 'John', surname = "Doe",
                               email = "example@gmail.com",
                               birthday = date(year = 1997, month = 9, day = 26),
                               data = 'body.data', user = self.user)

    async def test_get_all_contacts(self):
        result = [Contact(), Contact(), Contact()]
        self.session.query().filter_by().all.return_value = result
        func_res = await get_all_contacts(self.user, self.session)
        self.assertEqual(func_res, result)

    async def test_create_contact(self):
        body = ContactModel(name = self.contact.name,
                            surname = self.contact.surname,
                            email = self.contact.email,
                            birthday = self.contact.birthday,
                            data = self.contact.data,
                            user = self.contact.user)
        result = self.contact
        func_res = await create_contact(body, self.user, self.session)
        self.assertEqual(func_res.name, body.name)
        self.assertIsNot(func_res, result)
        self.assertEqual(func_res.email, body.email)
        self.assertTrue(hasattr(func_res, 'id'))

    async def test_get_one_contact(self):
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        result = await get_one_contact(self.contact.name, self.user, self.session)
        self.assertEqual(result, contact)

    async def test_get_one_contact_is_none(self):
        contact = None
        self.session.query().filter_by().first.return_value = None
        result = await get_one_contact(self.contact.name, self.user, self.session)
        self.assertEqual(result, contact)
        self.assertIsNone(result)

    async def test_del_contact(self):
        contact = Contact()
        self.session.query().filter_by.first.return_value = contact
        result = await del_contact(self.contact.name, self.user, self.session)
        self.assertIsNone(result)
        self.assertIsNot(result, contact)

    async def test_update_contact(self):
        contact = Contact()
        self.session.query().filter_by.first.return_value = contact
        new_body = self.contact
        self.contact.name = "Viktor"
        result = await update_contact(self.contact.name, new_body, self.user, self.session)
        self.assertTrue(hasattr(result, 'id'))
        self.assertEqual(result.name, new_body.name)
        self.assertEqual(result.surname, self.contact.surname)

if __name__ == '__main__':
    unittest.main()