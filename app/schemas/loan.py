from pydantic import BaseModel 
from datetime import date


class LoanCreate(BaseModel):
    book_id: int
    due_date: date
    
class LoanResponse(BaseModel):
    id : int
    user_id : int
    book_id : int
    borrow_issue_date : date
    due_date : date
    
    class Config:
        from_attributes = True 