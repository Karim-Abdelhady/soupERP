from enum import Enum

class BatchStatus(str, Enum):
    ACTIVE = "Active"
    ISSUED = "Issued"
    QUARANTINED = "Quarantined"
    EXPIRED = "Expired"

class SerialStatus(str,Enum):
    INSTOCK = "In stock"
    ISSUED = "Issued"
    UNDERREPAIR = "Under Repair"
    SCRAPPED = "Scrapped"