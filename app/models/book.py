from sqlalchemy import Column, Integer, String, CheckConstraint
from app.core.database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    isbn = Column(String(20), unique=True, nullable=False)
    stock = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("stock >= 0", name="check_stock_non_negative"),
    )
