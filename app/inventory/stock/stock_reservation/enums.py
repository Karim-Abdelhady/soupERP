from enum import Enum

class Status(str, Enum):
    ACTIVE = "Active"
    PARTIALLY = "Partially Fulfilled"
    FULFILLED = "Fulfilled"
    RELEASED = "Released"