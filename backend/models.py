from pydantic import BaseModel, EmailStr
from typing import Optional, List

class User(BaseModel):
    email: EmailStr
    password: str
    
class NewUser(BaseModel):
    name: str
    email: EmailStr
    password: str
    
class Movie(BaseModel):
    title: str
    year: Optional[int]
    cast: Optional[List[str]]
    plot: Optional[str]
