from fastapi import APIRouter,HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from app.schemas.loan import LoanCreate, LoanResponse
from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.loan import Loan
from app.models.user import User
from app.models.book import Book

router = APIRouter(prefix = '/loans', tags = ["Loans"])

@router.post("/borrow",
             response_model= LoanResponse,
             status_code=status.HTTP_201_CREATED)
def borrow_book(loan: LoanCreate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    
    book = db.query(Book).filter(Book.id == loan.book_id).first()
    
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found!")
    
    if book.stock <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book out of Stock!")
    
    existing_loan = db.query(Loan).filter(
        Loan.book_id == loan.book_id,
        Loan.user_id == current_user.id
    ).first()
    
    if existing_loan:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already borrowed this book!")
    
    new_loan = Loan(
        user_id = current_user.id,
        book_id = loan.book_id,
        borrow_issue_date = date.today(),
        due_date = loan.due_date
    )
    
    book.stock -= 1
    
    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    
    return new_loan

@router.post("return/{loan_id}", status_code= status.HTTP_200_OK)
def return_book(loan_id : int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found!")

    if loan.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can not return this book!")

    book = db.query(Book).filter(loan.book_id == Book.id).first()
    book.stock += 1
    
    db.delete(loan)
    db.commit()
    
    return {"message": "Book return successfully!"}

@router.get("/me", response_model=List[LoanResponse])
def my_loans(db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    return db.query(Loan).filter(current_user.id == Loan.user_id).all()