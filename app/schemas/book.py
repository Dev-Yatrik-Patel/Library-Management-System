from pydantic import BaseModel

class BookBase(BaseModel):
    name: str
    isbn: str
    stock: int
    
class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    pass
    class Config:
        from_attributes = True