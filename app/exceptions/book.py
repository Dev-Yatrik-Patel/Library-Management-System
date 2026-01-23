from app.exceptions.base import AppException

class BookNotFound(AppException):
    status_code = 404
    error_code = "BOOK_NOT_FOUND"
    message = "Book not found!"

class BookOutOfStock(AppException):
    status_code = 400
    error_code = "BOOK_OUT_OF_STOCK"
    message = "Book is out of stock!"
