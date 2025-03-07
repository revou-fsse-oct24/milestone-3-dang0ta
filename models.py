from pydantic import BaseModel

class UserInformation(BaseModel):
    name: str
    email: str

class UserCredential(UserInformation):    
    password: str