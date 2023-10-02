import pickle
from typing import Optional
from datetime import datetime, timedelta

import redis
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt

from src.db.db import get_db
from src.repository.users import get_user_by_email
from src.conf.config import settings


class Authorization:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    c = redis.Redis(host=settings.redis_host, port=settings.redis_port, password=settings.redis_password)

    def verify_password(self, plain_password, password: str):
        """
        The verify_password function takes a plain-text password and hashed
        password, and verifies that the plain-text password matches the hashed
        password. It returns True if they match, or False otherwise.
        
        :param self: Represent the instance of the class
        :param plain_password: Check the password that is entered by the user
        :param password: str: Verify the password
        :return: True if the password is correct and false otherwise
        """
        return self.pwd_context.verify(plain_password, password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password and returns the hashed version of that password.
        The hashing algorithm is defined in the config file, which is passed to CryptContext when it's created.
        
        :param self: Represent the instance of the class
        :param password: str: Pass in the password that is being hashed
        :return: A hash of the password
        """
        return self.pwd_context.hash(password)

    # Define function for new access token
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_access_token function creates a new access token.
            Args:
                data (dict): A dictionary of key-value pairs to include in the JWT payload.
                expires_delta (Optional[float]): An optional timedelta indicating how long the token should be valid for. Defaults to 15 minutes if not provided.
        
        :param self: Refer to the class itself
        :param data: dict: Pass in the data to be encoded
        :param expires_delta: Optional[float]: Set the expiration time of the access token
        :return: An encoded access token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        
        return encoded_access_token
    
    # Define function for new refresh token
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_refresh_token function creates a refresh token for the user.
            The function takes in two parameters: data and expires_delta.
            Data is a dictionary containing the user's email, username, and password. 
            Expires_delta is an optional parameter that sets how long until the refresh token expires.
        
        :param self: Represent the instance of the class
        :param data: dict: Pass in the user's id and username
        :param expires_delta: Optional[float]: Set the expiration time of the refresh token
        :return: A refresh token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    # Get current user
    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldn't validate credentials!", headers={"WWW-Authenticate": "Bearer"})

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])

            if payload.get("scope") == "access_token":
                email = payload.get("sub")
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        # user = await get_user_by_email(email, db)
        user = self.c.get(f"user:{email}")

        if user is None:
            user = await get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.c.set(f"user:{email}", pickle.dumps(user))
            self.c.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)

        if user is None:
            raise credentials_exception
        return user

    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function decodes the refresh token and returns the email of the user.
        If there is an error, it will raise a HTTPException with status code 401 (Unauthorized)
        
        :param self: Represent the instance of the class
        :param refresh_token: str: Pass in the refresh token that is sent from the frontend
        :return: The email of the user
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])

            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    def create_email_token(self, data: dict):
        """
        The create_email_token function creates a token that is used to verify the user's email address.
        The token is created using the JWT library and contains information about when it was issued, 
        when it expires, and what scope (or purpose) it has. The function returns this token.
        
        :param self: Make the function a method of the class
        :param data: dict: Pass in the data that will be encoded into a jwt
        :return: A token that is encoded with the user's email and a timestamp
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=1)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email associated with that token.
            If the scope of the payload is not 'email_token', then it raises an HTTPException.
            If there is a JWTError, then it also raises an HTTPException.
        
        :param self: Represent the instance of the class
        :param token: str: Pass in the token that is sent to the user's email address
        :return: The email address associated with the token
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])

            if payload['scope'] == 'email_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid token for email verification")


auth_service = Authorization()