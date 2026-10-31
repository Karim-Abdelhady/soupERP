from enum import Enum

class SessionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "logged out"
    INACTIVE = "inactive"   