from enum import Enum

class Purpose(str, Enum):
    TRANSFER = "Material Transfer"
    ISSUE = "Material Issue"
    RECEIPT = "Material Receipt"
    SCRAP = "Material Scrap"
    REPACK = "Repacks"
    MANUFACTURE = "Manufacture"
    SUBCONTRACTING = "Subcontracting"
    CONSUMPTION = "Material Consumption"

class Status(str, Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    CANCELED = "Canceled"