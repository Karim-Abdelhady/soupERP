from pydantic import BaseModel
from decimal import Decimal
from typing import List

class PaymentTermResponse(BaseModel):
    id: int
    name: str
    due_days: int
    is_active: bool

    class Config:
        from_attributes = True

class PaymentTermCreate(BaseModel):
    name: str
    due_days: int = 0

class PaymentTermUpdate(BaseModel):
    name: str | None = None
    due_days: int | None = None

class PaymentTermsTemplateLineResponse(BaseModel):
    id: int
    template_id: int
    payment_term_id: int
    invoice_portions: Decimal
    description: str | None = None

    class Config:
        from_attributes = True

class PaymentTermsTemplateResponse(BaseModel):
    id: int
    template_name: str
    is_active: bool

    lines: List[PaymentTermsTemplateLineResponse]

    class Config:
        from_attributes = True

class PaymentTermsTemplateLineCreate(BaseModel):
    payment_term_id: int
    invoice_portions: Decimal
    description: str | None = None

class PaymentTermsTemplateCreate(BaseModel):
    template_name: str

    lines: List[PaymentTermsTemplateLineCreate]

class PaymentTermsTemplateLineUpdate(BaseModel):
    payment_term_id: int | None = None
    invoice_portions: Decimal | None = None
    description: str | None = None

class PaymentTermsTemplateUpdate(BaseModel):
    template_name: str | None = None

    lines: List[PaymentTermsTemplateLineUpdate] | None = None

class Activation(BaseModel):
    is_active: bool