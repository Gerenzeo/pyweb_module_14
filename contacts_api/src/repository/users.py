from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.db.models import User
from src.schemas.users_schema import UserModel

async def get_user_by_email(email: str, db: Session) -> User | None:
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user associated with that email. If no such user exists, it
    returns None.
    
    :param email: str: Pass in the email of the user
    :param db: Session: Pass the database session into the function
    :return: A user object if a user with the given email exists in the database, otherwise it returns none
    """
    user = db.query(User).filter_by(email=email).first()
    return user

async def create_user(body: UserModel, db: Session):
    """
    The create_user function creates a new user in the database.
    
    :param body: UserModel: Pass the user model to the function
    :param db: Session: Pass the database session to the function
    :return: A new user object
    """
    new_user = User(**body.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

async def update_token(user: User, refresh_token, db: Session):
    """
    The update_token function takes in a user object, a refresh token string, and
    a database session. It then updates the user's refresh_token attribute to be
    the new value of the refresh_token parameter. Finally it commits this change to
    the database.
    
    :param user: User: Identify the user in the database
    :param refresh_token: Update the user's refresh token in the database
    :param db: Session: Pass the database session to the function
    :return: None
    """
    user.refresh_token = refresh_token
    db.commit()

async def change_password(email: str, new_password: str, db: Session):
    """
    The change_password function takes an email and a new password,
    and changes the user's password to the new one.
    
    
    :param email: str: Identify the user to change the password for
    :param new_password: str: Pass in the new password that the user wants to change their password to
    :param db: Session: Pass the database session to the function
    :return: Nothing
    """
    user = await get_user_by_email(email, db)
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user.password = pwd_context.hash(new_password)
    db.commit()

async def confirm_email(email: str, db: Session):
    """
    The confirm_email function takes an email and a database session as arguments.
    It then uses the get_user_by_email function to retrieve the user with that email from the database.
    The confirm_email function then sets that user's confirmed field to True, and commits those changes to the database.
    
    :param email: str: Get the email of the user
    :param db: Session: Access the database
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()

async def update_avatar(email: str, url: str, db: Session) -> User:
    """
    The update_avatar function takes an email and a url, and updates the avatar of the user with that email to be
    the given url. It returns the updated user.
    
    :param email: str: Specify the email of the user to update
    :param url: str: Pass the url of the avatar to be updated
    :param db: Session: Connect to the database
    :return: A user object
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user