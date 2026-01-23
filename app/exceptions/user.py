from app.exceptions.base import AppException

class UserNotFound(AppException):
    status_code = 404
    error_code = "USER_NOT_FOUND"
    message = "User not found"

class UserLoanPending(AppException):
    status_code = 400
    error_code = "USER_LOAN_PENDING"
    message = "Pending load detected!"

class UserEmailAlreadyExists(AppException):
    status_code = 400
    error_code = "USER_EMAIL_ALREADY_REGISTERED"
    message = "Email is already in use!"
