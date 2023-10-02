from pydantic import BaseModel

class ResetPassword(BaseModel):
    token: str
    new_password: str
    confirm_new_password: str
