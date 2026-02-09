from pydantic import BaseModel
from typing import Optional

class UserLogin(BaseModel):
    phone: str
    pin: str

class UserRegister(BaseModel):
    phone: str
    pin: str
    name: Optional[str] = "Janani User"
    
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    name: str

class UserProfile(BaseModel):
    user_id: str
    phone: str
    name: str
