from enum import Enum

class UserType(str, Enum):
    USER = "user"
    CUSTOMER = "customer"
    EMPLOYEE = "employee"
    ADMIN = "admin"