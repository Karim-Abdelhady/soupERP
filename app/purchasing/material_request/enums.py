from enum import Enum

class Status(str, Enum):
    DRAFT = "draft"
    SUBMIT = "submitted"
    ORDER = "ordered"
    CANCEL = "cancelled"

class MaterialRequestType(str, Enum):
    PURCHASE = "purchase"
    TRANSFER = "transfer"
    ISSUE = "issue"