from pydantic import BaseModel, EmailStr


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
    id: int
    role_id: int

    class Config:
        from_attributes = True
