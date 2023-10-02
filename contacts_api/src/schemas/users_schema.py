from typing import Optional

from pydantic import BaseModel, EmailStr


class UserModel(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    password: str
    avatar: Optional[str]

    class Config:
        from_attributes = True

