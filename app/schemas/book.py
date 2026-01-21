from pydantic import BaseModel

class BookBase(BaseModel):
    name: str
    isbn: str
    stock: int
    
class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    name: str | None = None
    isbn: str | None = None
    stock: int | None = None

class BookResponse(BookBase):
    id : int 
    
    class Config:
        from_attributes = True