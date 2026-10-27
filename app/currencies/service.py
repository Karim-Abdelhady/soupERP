from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.currencies import repository
from app.currencies.schemas import CurrencyUpdate, ExchangeRateUpdate, CurrencyCreate, ExchangeRateCreate
from app.currencies.models import Currency, ExchangeRate
from datetime import datetime, timezone

def get_currencies(db: Session):
    currencies = repository.get_currencies(db)
    if not currencies:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "No currencies were created")
    return currencies

def get_currency_by_id(db: Session, currency_id: int):
    currency = repository.get_currency_by_id(db, currency_id)
    if currency is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Currency with ID is not found")
    return currency

def create_currency(db: Session, new_currency: CurrencyCreate):
    existing_currency = repository.get_currency_by_code(db, new_currency.code)
    if existing_currency is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Currency is already created")

    db_data = new_currency.model_dump(exclude_unset=True)
    return repository.create_currency(db, db_data)

def update_currency(db: Session, currency_id: int, update_currency: CurrencyUpdate):
    currency = repository.get_currency_by_id(db, currency_id)
    if not currency:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Currency with ID is not found")

    db_data = update_currency.model_dump(exclude_unset=True)

    for key,value in db_data.items():
        setattr(currency, key, value)
    currency.updated_at = datetime.now(timezone.utc)

    updated = repository.update_currency(db, currency)
    return updated

def get_rates(db: Session):
    rates = repository.get_rates(db)
    if not rates:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "No rates were created")
    return rates

def get_rate_by_id(db: Session, rate_id: int):
    rate = repository.get_rate_by_id(db, rate_id)
    if rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Rate with ID is not found")
    return rate

def get_latest_rate(db: Session, rate_id: int):
    rate = repository.get_latest_rate(db, rate_id)
    if rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Rate with ID is not found")
    return rate

def create_rate(db: Session, new_rate: ExchangeRateCreate):
    db_data = new_rate.model_dump(exclude_unset=True)
    return repository.create_rate(db, db_data)

def update_rate(db: Session, rate_id: int, update_rate: ExchangeRateUpdate):
    rate = repository.get_rate_by_id(db, rate_id)
    if rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Rate with ID is not found")
    db_data = update_rate.model_dump(exclude_unset=True)

    for key,value in db_data.items():
        setattr(rate, key, value)
    rate.last_updated = datetime.now(timezone.utc)

    updated = repository.update_rate(db, rate)
    return updated

def convert_currency(db: Session, amount: float, rate_id: int):
    rate = repository.get_rate_by_id(db, rate_id)
    if rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Rate with ID is not found")
    if not rate.from_currency.is_active or not rate.to_currency.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "One of the currencies is not active")

    current_time = datetime.now(timezone.utc)

    if rate.effective_from and current_time < rate.effective_from:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Exchange rate is not still effective")
    if rate.effective_to and current_time > rate.effective_to:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Exchange rate has expired")
    
    result = amount * rate.rate

    return {
        "from_currency": rate.from_currency.code,
        "to_currency": rate.to_currency.code,
        "original_amount": amount,
        "exchange_rate": rate.rate,
        "converted_amount": round(result, int(rate.to_currency.decimal_places))
    }