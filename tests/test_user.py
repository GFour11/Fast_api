import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User
from src.repositories.operations import signup, update_avatar, confirmed_email
from src.schemas import UserModel

class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=193, email='test@gmail.com', password='1234',
                         access_token=None, refresh_token=None,
                         confirmed=False, avatar='qweqweq')




    # async def test_signup(self):
    #     body = UserModel(email='test2@gmail.com', password=self.user.password)
    #     result = await signup(body=body, db=self.session)
    #     self.assertEqual(result.email, body.email)


    async def test_signup_user_is_exist(self):
        detail = "User is all ready exist"
        body = UserModel(email=self.user.email, password=self.user.password)
        result = await signup(body, self.session)
        self.assertEqual(result.detail, detail)



    async def test_update_avatar(self):
        # user = User()
        self.session.query().filter_by().first.return_value = self.user
        url = 'new_url'
        expected_user = User(id=123, email='test@gmail.com', password='1234',
                             access_token=None, refresh_token=None,
                             confirmed=False, avatar='qweqweq')
        self.session.commit.return_value = None
        result = await update_avatar(self.user.email, url, self.session)
        self.assertEqual(result.avatar, url)
        self.assertEqual(expected_user.email, result.email)

    async def test_email_confirmed(self):
        self.session.query().filter_by().first.return_value = self.user
        result = await confirmed_email(self.user.email, self.session)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
