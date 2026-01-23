from app.exceptions.base import AppException

class AuthenticationError(AppException):
    status_code = 401
    error_code = "AUTHENTICATION_FAILED"
    message = "Authentication failed. Please try again."

class AuthorizationError(AppException):
    status_code = 403
    error_code = "AUTHORIZATION_FAILED"
    message = "Authorization failed. Please try again."
    
class MyHTTPException(AppException):
    status_code = 401
    error_code = "AUTHENTICATION_FAILED"
    message = "Cound not validate Credentials"
     