from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from app.currencies.models import Currency, ExchangeRate

def get_currencies(db: Session):
    statement = select(Currency)
    return db.scalars(statement).all()

def get_currency_by_id(db: Session, currency_id: int):
    statement = select(Currency).where(Currency.id == currency_id)
    return db.scalar(statement)

def get_currency_by_code(db: Session, currency_code: str):
    statement = select(Currency).where(Currency.code == currency_code)
    return db.scalar(statement)

def create_currency(db: Session, new_currency: Currency):
    db_data = Currency(**new_currency)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

def update_currency(db: Session, update_currency: Currency):
    db.commit()
    db.refresh(update_currency)
    return update_currency

def get_rates(db: Session):
    statement = select(ExchangeRate)
    return db.scalars(statement).all()

def get_rate_by_id(db: Session, rate_id: int):
    statement = select(ExchangeRate).where(ExchangeRate.id == rate_id)
    return db.scalar(statement)    

def get_latest_rate(db: Session, rate_id: int):
    statement = (
        select(ExchangeRate)
        .where(ExchangeRate.id == rate_id)
        .order_by(desc(ExchangeRate.last_updated))
        .limit(1)
    )
    return db.scalar(statement)

def create_rate(db: Session, new_rate: ExchangeRate):
    db_data = ExchangeRate(**new_rate)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

def update_rate(db: Session, update_rate: ExchangeRate):
    db.commit()
    db.refresh(update_rate)
    return update_rate

