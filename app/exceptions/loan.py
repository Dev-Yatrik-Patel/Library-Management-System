from app.exceptions.base import AppException

class AlreadyBorrowed(AppException):
    pass

class LoanNotFound(AppException):
    pass

class InvalidLoanOperation(AppException):
    pass