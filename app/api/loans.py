from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.loan import LoanCreate, LoanResponse

from app.controllers.auth_controller import get_current_user

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.core.roles import Roles 
from app.core.response import success_response

from app.models.user import User

from app.controllers.loan_controller import (
    borrow_book_user,
    return_book_user,
    active_loans_users,
    my_loan_history_user,
    user_loan_history_admin)

router = APIRouter(prefix = '/loans', tags = ["Loans"])

@router.post("/borrow",
             response_model= LoanResponse,
             status_code=status.HTTP_201_CREATED)
def borrow_book(loan: LoanCreate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    new_loan = borrow_book_user(loan = loan, current_user = current_user, db = db )
    return success_response(
        data = LoanResponse.model_validate(new_loan).model_dump(mode="json")
    )

@router.post("return/{loan_id}", status_code= status.HTTP_200_OK)
def return_book(loan_id : int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return_book_user(loan_id= loan_id, db = db, current_user = current_user)
    return success_response(message="Book return successfully!")

@router.get("/me", response_model=List[LoanResponse])
def my_active_loans(db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    activeLoanRecords = active_loans_users(db = db, current_user = current_user )
    return success_response(
        data = [ LoanResponse.model_validate(i).model_dump(mode="json") for i in activeLoanRecords]
    )

@router.get("/history", response_model=List[LoanResponse])
def my_loan_history(db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    historyLoanRecords = my_loan_history_user(db = db, current_user = current_user)
    return success_response(
        data = [ LoanResponse.model_validate(i).model_dump(mode="json") for i in historyLoanRecords]
    )

@router.get("/user/{user_id}",
            response_model=List[LoanResponse],
            dependencies=[Depends(require_roles(Roles.ADMIN,Roles.LIBRARIAN))])
def user_loan_history(user_id: int, db: Session = Depends(get_db) ):
    userLoanHistory = user_loan_history_admin(user_id = user_id, db = db)
    return success_response(
        data = [ LoanResponse.model_validate(i).model_dump(mode="json") for i in userLoanHistory]
    )
