from fastapi import APIRouter,HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from app.schemas.loan import LoanCreate, LoanResponse
from app.api.auth import get_current_user

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.core.roles import Roles 

from app.models.loan import Loan
from app.models.user import User
from app.models.book import Book

from app.exceptions.book import BookNotFound, BookOutOfStock
from app.exceptions.auth import AuthenticationError, AuthorizationError
from app.exceptions.loan import AlreadyBorrowed, InvalidLoanOperation, LoanNotFound

router = APIRouter(prefix = '/loans', tags = ["Loans"])

@router.post("/borrow",
             response_model= LoanResponse,
             status_code=status.HTTP_201_CREATED)
def borrow_book(loan: LoanCreate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    
    book = db.query(Book).filter(Book.id == loan.book_id).first()
    
    if not book:
        raise BookNotFound("Book not found!")
        
    if book.stock <= 0:
        raise BookOutOfStock("Book out of Stock!")
    
    existing_loan = db.query(Loan).filter(
        Loan.book_id == loan.book_id,
        Loan.user_id == current_user.id,
        Loan.is_active == True
    ).first()
    
    if existing_loan:
        raise AlreadyBorrowed("You have already borrowed this book!")
    
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
    loan = db.query(Loan).filter(Loan.id == loan_id, Loan.is_active == True).first()
    
    if not loan:
        raise LoanNotFound("Loan not found!")

    if loan.user_id != current_user.id:
        raise InvalidLoanOperation("You can not return this book!")

    book = db.query(Book).filter(loan.book_id == Book.id).first()
    
    loan.is_active = False
    loan.returned_at = date.today()
    book.stock += 1
    
    db.commit()
    
    return {"message": "Book return successfully!"}

@router.get("/me", response_model=List[LoanResponse])
def my_active_loans(db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    return db.query(Loan).filter(current_user.id == Loan.user_id, Loan.is_active == True).all()

@router.get("/history", response_model=List[LoanResponse])
def my_loan_history(db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    return db.query(Loan).filter(current_user.id == Loan.user_id).all()

@router.get("/user/{user_id}",
            response_model=List[LoanResponse],
            dependencies=[Depends(require_roles(Roles.ADMIN,Roles.LIBRARIAN))])
def user_loan_history(user_id: int, db: Session = Depends(get_db) ):
    return db.query(Loan).filter(Loan.user_id == user_id).all()
