from sqlalchemy import Column, Integer, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    borrow_issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    
    returned_at = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)

    user = relationship("User")
    book = relationship("Book")
