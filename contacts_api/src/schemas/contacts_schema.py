from datetime import datetime, date
from pydantic import BaseModel, Field, EmailStr, validator


class ContactModel(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    birthday: date
    email: EmailStr
    phone: str = Field(min_length=10, max_length=12)
    favorite: bool

    @validator("phone")
    def validate_digits(cls, phone):
        if not phone.isdigit():
            raise ValueError("Phone number should only contain digits")
        return phone


class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    birthday: date
    email: EmailStr
    phone: str
    favorite: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
