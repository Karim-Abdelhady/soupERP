from pydantic import BaseModel
from datetime import datetime

class CurrencyCreate(BaseModel):
    code: str
    name: str
    symbol: str | None = None
    decimal_places: float
    is_active: bool
    is_system: bool | None = None

class CurrencyResponse(BaseModel):
    id: int
    code: str
    name: str
    symbol: str | None = None
    decimal_places: float
    is_active: bool
    is_system: bool | None = None
    created_at: datetime
    updated_at: datetime
    created_by: str

    class Config:
        from_attributes = True

class CurrencyUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    symbol: str | None = None
    decimal_places: float | None = None
    is_active: bool | None = None
    is_system: bool | None = None

class ExchangeRateCreate(BaseModel):
    from_currency_id: int
    to_currency_id: int
    rate: float
    source: str
    effective_from: datetime
    effective_to: datetime | None = None

class ExchangeRateResponse(BaseModel):
    id: int
    from_currency_id: int
    to_currency_id: int
    rate: float
    source: str
    effective_from: datetime
    effective_to: datetime | None = None
    last_updated: datetime

    class Config:
        from_attributes = True

class ExchangeRateUpdate(BaseModel):
    from_currency_id: int | None = None
    to_currency_id: int | None = None
    rate: float | None = None
    source: str | None = None
    effective_from: datetime | None = None
    effective_to: datetime | None = None

class CurrencyConversionResponse(BaseModel):
    from_currency: str
    to_currency: str
    original_amount: float
    exchange_rate: float
    converted_amount: float

    class Config:
        from_attributes = True