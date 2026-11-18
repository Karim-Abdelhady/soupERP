from enum import Enum

class ReservationStatus(str, Enum):
    ACTIVE = "active"
    PARTIALLY = "partially fulfilled"
    FULFILLED = "fulfilled"
    RELEASED = "released"