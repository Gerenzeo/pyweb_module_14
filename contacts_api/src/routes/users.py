from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from src.db.db import get_db
from src.db.models import User
from src.schemas.users_schema import UserResponse
from src.services.auth import auth_service
from src.services.cloudinary_service import CloudImage
from src.repository.users import update_avatar

router = APIRouter(prefix="/users", tags=['users'])

@router.get("/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_users_me function is a GET request that returns the current user's information.
        The function takes in a User object, which is passed to it by the auth_service module.
        This User object contains all of the information about the current user, and this function simply returns it.
    
    :param current_user: User: Get the current user
    :return: The current user
    """
    return current_user

@router.put('/avatar', response_model=UserResponse)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    """
    The update_avatar_user function takes a file and the current user as input.
    It then uploads the file to Cloudinary, generates a public_id for it, and gets its src_url.
    Finally, it updates the avatar of the current user with this new src_url.
    
    :param file: UploadFile: Get the file from the request
    :param current_user: User: Get the current user
    :param db: Session: Get a database session, which is required for interacting with the database
    :return: The user object
    """
    public_id = CloudImage.genereate_name_avatar(current_user.email)
    r = CloudImage.upload(file.file, public_id)
    src_url = CloudImage.get_url_for_avatar(public_id, r)
    user = await update_avatar(current_user.email, src_url, db)
    return user

