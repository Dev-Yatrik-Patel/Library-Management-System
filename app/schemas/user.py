from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str
    role_id: int

class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role_id: int

     
