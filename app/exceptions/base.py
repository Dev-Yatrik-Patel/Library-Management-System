class AppException(Exception):
    status_code = 400
    error_code = "APP_ERROR"
    message = "Application error"

    def __init__(self, message: str | None = None):
        if message:
            self.message = message
