from sqlalchemy.orm import Session
from datetime import date

from app.models.loan import Loan
from app.models.user import User
from app.models.book import Book

from app.schemas.loan import LoanCreate
from app.schemas.audit_logs import AuditAction

from app.core.audit import log_audit

from app.exceptions.book import BookNotFound, BookOutOfStock
from app.exceptions.loan import AlreadyBorrowed, InvalidLoanOperation, LoanNotFound

def borrow_book_user(loan: LoanCreate,
                current_user: User,
                db: Session):
    
    book = db.query(Book).filter(Book.id == loan.book_id).first()
    
    if not book:
        raise BookNotFound()
        
    if book.stock <= 0:
        raise BookOutOfStock()
    
    existing_loan = db.query(Loan).filter(
        Loan.book_id == loan.book_id,
        Loan.user_id == current_user.id,
        Loan.is_active == True
    ).first()
    
    if existing_loan:
        raise AlreadyBorrowed(message = "You have already borrowed this book!")
    
    new_loan = Loan(
        user_id = current_user.id,
        book_id = loan.book_id,
        borrow_issue_date = date.today(),
        due_date = loan.due_date
    )
    
    book.stock -= 1
    
    db.add(new_loan)
    db.flush()
    
    # Audit loan creation
    log_audit(
        db,
        action=AuditAction.LOAN_CREATED,
        entity="Loan",
        entity_id=new_loan.id,
        performed_by=current_user.id,
        message=f"User {current_user.email} took book by himself/herself."
    )
    
    db.commit()
    db.refresh(new_loan)
    
    return new_loan

def return_book_user(loan_id : int,
                db: Session,
                current_user: User):
    loan = db.query(Loan).filter(Loan.id == loan_id, Loan.is_active == True).first()
    
    if not loan:
        raise LoanNotFound()

    if loan.user_id != current_user.id:
        raise InvalidLoanOperation(message = "You can not return this book!")

    book = db.query(Book).filter(loan.book_id == Book.id).first()
    
    loan.is_active = False
    loan.returned_at = date.today()
    book.stock += 1
    
    # Audit loan creation
    log_audit(
        db,
        action=AuditAction.LOAN_RETURNED,
        entity="Loan",
        entity_id=loan.id,
        performed_by=current_user.id,
        message=f"User {current_user.email} returned book by himself/herself."
    )
    
    db.commit()
    
    return 

def active_loans_users(db: Session, current_user: User):
    activeLoanRecords = db.query(Loan).filter(current_user.id == Loan.user_id, Loan.is_active == True).all()
    return activeLoanRecords

def my_loan_history_user(db: Session,current_user: User):
    historyLoanRecords = db.query(Loan).filter(current_user.id == Loan.user_id).all()
    return historyLoanRecords

def user_loan_history_admin(user_id: int, db: Session):
    userLoanHistory = db.query(Loan).filter(Loan.user_id == user_id).all()
    return userLoanHistory
    