from fastapi import APIRouter, Depends
from database.database import get_db
from app.purchasing.payment_terms import service
from app.purchasing.payment_terms.schemas import PaymentTermCreate, PaymentTermsTemplateCreate, PaymentTermUpdate, PaymentTermsTemplateUpdate, PaymentTermResponse, PaymentTermsTemplateResponse, Activation
from typing import List
from sqlalchemy.orm import Session
router = APIRouter()

@router.get("/paymentterms/", response_model = List[PaymentTermResponse], tags = ["Payment Terms"])
def get_payment_terms(db: Session = Depends(get_db)):
    return service.get_payment_terms(db)

@router.get("/paymentterms/{term_id}", response_model=PaymentTermResponse, tags = ["Payment Terms"])
def get_payment_term_by_id(term_id: int, db: Session = Depends(get_db)):
    return service.get_payment_term_by_id(db, term_id)

@router.get("/paymenttermstemplates/", response_model=List[PaymentTermsTemplateResponse], tags = ["Payment Terms"])
def get_payment_terms_templates(db: Session = Depends(get_db)):
    return service.get_payment_terms_templates(db)

@router.get("/paymenttermstemplates/{template_id}/", response_model=PaymentTermsTemplateResponse, tags = ["Payment Terms"])
def get_payment_terms_template_by_id(template_id: int, db: Session = Depends(get_db)):
    return service.get_payment_terms_template_by_id(db, template_id)

@router.post("/paymentterms/", response_model = PaymentTermResponse, tags = ["Payment Terms"])
def create_payment_term(new_term: PaymentTermCreate, db: Session = Depends(get_db)):
    return service.create_payment_term(db, new_term)

@router.patch("/paymentterms/{term_id}", response_model = PaymentTermResponse, tags = ["Payment Terms"])
def update_payment_term(term_id: int, update_term: PaymentTermUpdate, db: Session = Depends(get_db)):
    return service.update_payment_term(db, term_id, update_term)

@router.post("/paymenttermstemplates/", response_model= PaymentTermsTemplateResponse, tags = ["Payment Terms"])
def create_payment_term_template(new_template: PaymentTermsTemplateCreate, db: Session = Depends(get_db)):
    return service.create_payment_term_template(db, new_template)

@router.patch("/paymenttermstemplates/{template_id}", response_model = PaymentTermsTemplateResponse, tags = ["Payment Terms"])
def update_payment_term_template(template_id: int, update_template: PaymentTermsTemplateUpdate, db: Session = Depends(get_db)):
    return service.update_payment_term_template(db, template_id, update_template)

@router.patch("/paymentterms/{term_id}/activate/", response_model = Activation, tags = ["Payment Terms"])
def activate_payment_term(term_id: int, activate: Activation, db: Session = Depends(get_db)):
    return service.activate_payment_term(db, term_id, activate)

@router.patch("/paymenttermstemplate/{template_id}/activate/", response_model = Activation, tags = ["Payment Terms"])
def activate_payment_term_template(template_id: int, activate: Activation, db: Session = Depends(get_db)):
    return service.activate_payment_term_template(db, template_id, activate)
