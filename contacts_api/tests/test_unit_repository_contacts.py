import datetime
import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.db.models import User, Contact
from src.schemas.contacts_schema import ContactModel
from src.repository.contacts import (
    get_contacts,
    create_contact,
    get_contact_by_id,
    update_contact,
    remove_contact,
)


contact_model = ContactModel(
            first_name="michael",
            last_name="mayers",
            birthday=datetime.datetime(year=2000, month=1, day=1),
            email='michael_mayers@mail.com',
            phone="380501112233",
            favorite=True
        )


class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await get_contacts(user_id=self.user.id, db=self.session)
        self.assertEqual(result, contacts)

    async def test_create_contact(self):
        body = contact_model
        result = await create_contact(user_id=self.user.id, body=body, db=self.session)

        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.birthday, body.birthday)

    async def test_get_contact_by_id(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact_by_id(contact_id=1, user_id=self.user.id, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_by_id_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact_by_id(contact_id=1, user_id=self.user.id, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact(self):
        contact = contact_model
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, user_id=self.user.id, body=contact, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        contact = contact_model
        self.session.query().filter().first.return_value = None
        result = await update_contact(contact_id=1, user_id=self.user.id, body=contact, db=self.session)
        self.assertIsNone(result)

    async def test_remove_contact(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user_id=self.user.id, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user_id=self.user.id, db=self.session)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()