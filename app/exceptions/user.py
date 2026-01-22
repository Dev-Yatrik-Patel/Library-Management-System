from app.exceptions.base import AppException

class UserNotFound(AppException):
    pass

class UserLoanPending(AppException):
    pass

class UserEmailAlreadyExists(AppException):
    pass