from enum import Enum

class Roles(str, Enum):
    ADMIN = "Admin"
    LIBRARIAN = "Librarian"
    STUDENT = "Student"
