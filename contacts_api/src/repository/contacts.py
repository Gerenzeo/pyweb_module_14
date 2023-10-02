from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.db.models import Contact
from src.schemas.contacts_schema import ContactModel




async def get_contacts(user_id: int, db: Session):
    """
    Return all contacts from database.

    :param user_id: For wich user id get all contacts
    :type user_id: int
    :param db: database session
    :type db: Session
    :return: All contacts for set user_id
    :rtype: [Contacts] | []
    """
    contacts = db.query(Contact).filter(Contact.contact_owner_id == user_id).all()
    return contacts

async def create_contact(user_id: int, body: ContactModel, db: Session):
    """
    Create Contact to database.

    :param user_id: For wich user id will create contact
    :type user_id: int
    :param body: Contact fields
    :type body: ContactModel
    :param db: database session
    :type db: Session
    :return: Created Contact
    :rtype: 201 | None
    """
    contact = Contact(**body.dict())
    contact.contact_owner_id = user_id
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

async def get_contact_by_id(contact_id: int, user_id: int, db: Session):
    """
    Return Conctact by id from database
    
    :param contact_id: Contact id for searching
    :type contact_id: int
    :param user_id: For wich user id get all contacts
    :type user_id: int
    :param db: database session
    :type db: Session
    :return: Contact with searching id
    :rtype: Contact
    """
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.contact_owner_id == user_id).first()
    return contact


async def update_contact(contact_id: int, user_id: int, body: ContactModel, db: Session):
    """
    Update contact in database.
    
    :param contact_id: Contact id for deleting
    :type contact_id: int
    :param user_id: For wich user id get all contacts
    :type user_id: int
    :param body: Fields for updating
    :type body: ContactModel
    :param db: database session
    :type db: Session
    :return: Updated Contact
    :rtype: Contact
    """
    contact = await get_contact_by_id(contact_id, user_id, db)
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.birthday = body.birthday
        contact.email = body.email
        contact.phone = body.phone
        contact.favorite = body.favorite
        db.commit()
    return contact


async def remove_contact(contact_id:int, user_id: int, db: Session):  
    """
    Remove contact from database.
    
    :param contact_id: Contact id for deleting
    :type contact_id: int
    :param user_id: For wich user id get all contacts
    :type user_id: int
    :param db: database session
    :type db: Session
    :return: Status code 204 - No content
    :rtype: None
    """
    contact = await get_contact_by_id(contact_id, user_id, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact
