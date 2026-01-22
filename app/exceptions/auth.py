from app.exceptions.base import AppException

class AuthenticationError(AppException):
    pass

class AuthorizationError(AppException):
    pass