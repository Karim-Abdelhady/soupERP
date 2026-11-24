from enum import Enum

class UserType(str, Enum):
    USER = "user"
    CUSTOMER = "customer"
    SUPPLIER = "supplier"
    EMPLOYEE = "employee"
    ADMIN = "admin"