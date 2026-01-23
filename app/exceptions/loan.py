from app.exceptions.base import AppException

class AlreadyBorrowed(AppException):
    status_code = 400
    error_code = "ALREADY_BORROWED"
    message = "Already Borrowed!"

class LoanNotFound(AppException):
    status_code = 400
    error_code = "LOAN_NOT_FOUND"
    message = "Loan not found!"

class InvalidLoanOperation(AppException):
    status_code = 400
    error_code = "ALREADY_BORROWED"
    message = "Invalid Loan Operation!"