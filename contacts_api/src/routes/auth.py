from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.db.db import get_db
from src.schemas.email_schema import RequestEmail
from src.schemas.users_schema import UserModel, UserResponse
from src.schemas.tokens_schema import TokenModel
from src.repository.users import create_user, get_user_by_email, update_token, confirm_email, change_password
from src.services.auth import auth_service
from src.services.email_service import send_email, reset_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    The signup function creates a new user in the database.
        It takes a UserModel object as input, and returns the newly created user.
        If an account with that email already exists, it raises an HTTPException.
    
    :param body: UserModel: Get the data from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url for sending the email
    :param db: Session: Get the database session
    :return: A new user
    """
    exist_user = await get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Account already exist")

    body.password = auth_service.get_password_hash(body.password)
    new_user = await create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post('/login', response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    The login function is used to authenticate a user.
    It takes in the username and password of the user, and returns an access token if successful.
    
    
    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: Session: Get the database session
    :return: A dictionary with the access_token, refresh_token and token type
    """
    user = await get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes in the token that was sent to the user's email and uses it to get their email address.
        Then, it checks if there is a user with that email in the database, and if not, returns an error message.
        If there is a user with that email in the database, then we check whether or not they have already confirmed their account. 
            If they have already confirmed their account (i.e., if 'confirmed' == True), then we return another helpful message saying so; 
            otherwise (i.e
    
    :param token: str: Get the token from the url
    :param db: Session: Access the database
    :return: A message confirming that the user's email has been confirmed
    """
    email = auth_service.get_email_from_token(token)
    user = await get_user_by_email(email, db)

    if user.email is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await confirm_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    The request_email function is used to send an email to the user with a link that they can click on
    to confirm their email address. The function takes in a RequestEmail object, which contains the user's
    email address, and uses this information to find the corresponding UserModel object in our database. If 
    the UserModel exists (i.e., if there is already an account associated with that email), then we check whether 
    the account has been confirmed yet or not; if it hasn't been confirmed yet, then we add a task for sending 
    an email confirmation message using Celery.
    
    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks
    :param request: Request: Get the base_url of the request
    :param db: Session: Get a database session
    :return: A message to the user
    """
    user = await get_user_by_email(body.email, db)
    if user:
        if user.confirmed:
            return {"message": "Your email is already confirmed"}
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}


@router.post('/request_reset_password')
async def request_reset_password(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                                 db: Session = Depends(get_db)):
    """
    The request_reset_password function is used to request a password reset for the user with the given email.
        The function will send an email to that user containing a link which they can use to reset their password.
        This endpoint does not require authentication.
    
    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Run the reset_password function in a background thread
    :param request: Request: Get the base url of the application
    :param db: Session: Connect to the database
    :return: A message to the user that we have sent a new password on his email
    """
    user = await get_user_by_email(body.email, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User not found!')

    background_tasks.add_task(reset_password, user.email, user.username, str(request.base_url))
    return {"message": "We send new password on your email!"}


@router.post('/set_new_password/{token}')
async def set_new_password(token: str, new_password: str, confirm_new_password: str, db: Session = Depends(get_db)):
    """
    The set_new_password function takes in a token, new_password and confirm_new_password.
    It then gets the email from the token using auth service. It then gets the user by email from db.
    If there is no user with that email it raises an error 400 bad request saying verification error. If passwords do not match it raises an error 400 bad request saying passwords not same.
    
    :param token: str: Get the email from the token
    :param new_password: str: Set the new password for the user
    :param confirm_new_password: str: Ensure that the user has entered the same password twice
    :param db: Session: Access the database
    :return: A dict with a message
    """
    email = auth_service.get_email_from_token(token)
    user = await get_user_by_email(email, db)

    if user.email is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")

    if not new_password == confirm_new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords not same")

    await change_password(email, new_password, db)
    return {"message": "Password successfully changed"}


