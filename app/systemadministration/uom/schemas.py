from pydantic import BaseModel
from datetime import datetime

class UomCreate(BaseModel):
    code: str
    name: str
    symbol: str | None = None
    description: str | None = None
    must_be_whole_number: bool
    is_active: bool

class UomResponse(BaseModel):
    id: int
    code: str
    name: str
    symbol: str | None = None
    description: str | None = None
    must_be_whole_number: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: str

    class Config:
        from_attributes = True

class UomUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    symbol: str | None = None
    description: str | None = None
    must_be_whole_number: bool | None = None
    is_active: bool | None = None

class UnitConversionCreate(BaseModel):
    from_uom_id: int
    to_uom_id: int
    factor: float
    is_active: bool

class UnitConversionResponse(BaseModel):
    id: int
    from_uom_id: int
    to_uom_id: int
    factor: float
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UnitConversionUpdate(BaseModel):
    from_uom_id: int | None = None
    to_uom_id: int | None = None
    factor: float | None = None
    is_active: bool | None = None

class ConversionResponse(BaseModel):
    from_uom: str
    to_uom: str
    result: float
    unit_conversion: float
    converted_unit: float

    class Config:
        from_attributes = True