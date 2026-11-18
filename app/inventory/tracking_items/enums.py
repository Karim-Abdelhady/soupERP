from enum import Enum

class BatchStatus(str, Enum):
    ACTIVE = "active"
    ISSUED = "issued"
    QUARANTINED = "quarantined"
    EXPIRED = "expired"

class SerialStatus(str, Enum):
    ACTIVE = "active"
    IDLE = "idle"
    INSTOCK = "in stock"
    EXPIRED = "expired"

    def __str__(self) -> str:
        return self.value