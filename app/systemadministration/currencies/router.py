from fastapi import APIRouter, Depends
from database.database import get_db
from sqlalchemy.orm import Session
from app.systemadministration.currencies import service
from app.systemadministration.currencies.schemas import ExchangeRateResponse, CurrencyResponse, CurrencyCreate, CurrencyUpdate, ExchangeRateCreate, ExchangeRateUpdate, CurrencyConversionResponse
from typing import List

router = APIRouter()

@router.get("/currencies/", response_model = List[CurrencyResponse], tags = ["Currencies"])
def get_currencies(db: Session = Depends(get_db)):
    return service.get_currencies(db)

@router.get("/currencies/{currency_id}", response_model=CurrencyResponse, tags = ["Currencies"])
def get_currency_by_id(currency_id: int, db: Session = Depends(get_db)):
    return service.get_currency_by_id(db, currency_id)

@router.post("/currencies/", response_model=CurrencyResponse, tags = ["Currencies"])
def create_currency(new_currency: CurrencyCreate, db: Session = Depends(get_db)):
    return service.create_currency(db, new_currency)

@router.patch("/currencies/{currency_id}/", response_model=CurrencyResponse, tags = ["Currencies"])
def update_currency(currency_id: int, update_currency: CurrencyUpdate, db: Session = Depends(get_db)):
    return service.update_currency(db, currency_id, update_currency)

@router.get("/exchangerates/", response_model=List[ExchangeRateResponse], tags = ["ExchangeRates"])
def get_rates(db: Session = Depends(get_db)):
    return service.get_rates(db)

@router.get("/exchangerates/{rate_id}/", response_model=ExchangeRateResponse, tags = ["ExchangeRates"])
def get_rate_by_id(rate_id: int, db: Session = Depends(get_db)):
    return service.get_rate_by_id(db, rate_id)

@router.get("/exchangerates/{rate_id}/latest/", response_model=ExchangeRateResponse, tags = ["ExchangeRates"])
def get_latest_rate(rate_id: int, db: Session = Depends(get_db)):
    return service.get_latest_rate(db, rate_id)

@router.post("/exchangerates/", response_model=ExchangeRateResponse, tags = ["ExchangeRates"])
def create_rate(new_rate: ExchangeRateCreate, db: Session = Depends(get_db)):
    return service.create_rate(db, new_rate)

@router.patch("/exchangerates/{rate_id}/", response_model=ExchangeRateResponse, tags = ["ExchangeRates"])
def update_rate(rate_id: int, update_rate: ExchangeRateUpdate, db: Session = Depends(get_db)):
    return service.update_rate(db, rate_id, update_rate)

@router.post("/exchangerates/convert/{rate_id}/{amount}", response_model= CurrencyConversionResponse, tags = ["ExchangeRates"])
def convert_currency(rate_id: int, amount: float, db: Session = Depends(get_db)):
    return service.convert_currency(db, amount, rate_id)