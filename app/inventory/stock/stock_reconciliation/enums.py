from enum import Enum

class Status(str, Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    CANCELED = "Canceled"