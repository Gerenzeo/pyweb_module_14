from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

from src.db.db import engine

Base = declarative_base()

class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birthday = Column(DateTime)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(30), unique=True, nullable=False)
    favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), updated_at=func.now())
    contact_owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, default=1)
    contact_owner = relationship("User", backref="contacts")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(200), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    registration_date = Column(DateTime, default=func.now())
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    avatar = Column(String(255), default="no-image.jpg")


Base.metadata.create_all(bind=engine)