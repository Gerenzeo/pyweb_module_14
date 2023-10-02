import os
from pydantic import BaseModel

from dotenv import load_dotenv


load_dotenv()

class Settings(BaseModel):
    sqlalchemy_database_url: str = os.getenv('SQLALCHEMY_DATABASE_URL', 'postgresql+psycopg2://user:password@localhost:5432/postgres')
    secret_key: str = os.getenv("SECRET_KEY", 'secret_key')
    algorithm: str = os.getenv("ALGORITHM", 'HS256')
    mail_username: str = os.getenv("MAIL_USERNAME", 'example@mail.com')
    mail_password: str = os.getenv("MAIL_PASSWORD", 'password')
    mail_from: str = os.getenv("MAIL_FROM", 'example@mail.com')
    mail_port: int = os.getenv("MAIL_PORT", 465)
    mail_server: str = os.getenv("", 'smtp.meta.ua')
    redis_host: str = os.getenv("REDIS_HOST", 'localhost')
    redis_port: int = os.getenv("REDIS_PORT", 6379)
    redis_password: int = os.getenv("REDIS_PASSWORD", 'password')
    cloudinary_name: str = os.getenv("CLOUDINARY_NAME", "sa@5-3123df_fd")
    cloudinary_api_key: int = os.getenv("CLOUDINARY_API_KEY", "37927498275972984")
    cloudinary_api_secret: str = os.getenv("CLOUDINARY_API_SECRET", '********')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()