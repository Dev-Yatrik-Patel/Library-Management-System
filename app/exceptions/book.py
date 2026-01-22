from app.exceptions.base import AppException

class BookNotFound(AppException):
    pass


class BookOutOfStock(AppException):
    pass
