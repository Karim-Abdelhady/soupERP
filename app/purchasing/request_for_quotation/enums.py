from enum import Enum

class Status(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PARTIAL = "partial quoted"
    QUOTED = "quoted"
    CANCELLED = "cancelled"

class ResponseStatus(str, Enum):
    PENDING = "pending"
    RESPONDED = "responded"
    DECLINED = "declined" 