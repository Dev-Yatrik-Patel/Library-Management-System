from pydantic import BaseModel,ConfigDict

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
    model_config = ConfigDict(from_attributes=True)
    id : int 