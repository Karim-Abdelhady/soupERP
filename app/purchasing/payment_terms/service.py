from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.purchasing.payment_terms import repository
from app.purchasing.payment_terms.schemas import PaymentTermCreate, PaymentTermsTemplateCreate, PaymentTermUpdate, PaymentTermsTemplateUpdate, Activation
from decimal import Decimal
from app.purchasing.payment_terms.models import PaymentTerm, PaymentTermsTemplate, PaymentTermsTemplateLine


def get_payment_terms(db: Session):
    terms = repository.get_payment_terms(db)
    if not terms:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "No Payment Terms were found")
    return terms

def get_payment_term_by_id(db: Session, term_id: int):
    term = repository.get_payment_term_by_id(db, term_id)
    if term is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Payment Term ID is not found")
    return term

def get_payment_terms_templates(db: Session):
    templates = repository.get_payment_terms_templates(db)
    if not templates:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "No Templates were found")
    return templates

def get_payment_terms_template_by_id(db: Session, template_id: int):
    template = repository.get_payment_terms_template_by_id(db, template_id)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Payment Term Template ID is not found")
    return template

def create_payment_term(db: Session, new_term: PaymentTermCreate):
    if new_term.due_days < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Due Days can not be negative")
    new_data = new_term.model_dump(exclude_unset=True)
    new_data["is_active"] = True
    return repository.create_payment_term(db, new_data)

def update_payment_term(db: Session, term_id: int, update_term: PaymentTermUpdate):
    term = repository.get_payment_term_by_id(db, term_id)
    if term is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Payment Term ID is not found")
    if not term.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Payment Term can not be update because it is inactive")
    if update_term.due_days is not None and update_term.due_days < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Due days can not be negative")
    update_data = update_term.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(term, key, value)

    return repository.update_payment_term(db, term)

def create_payment_term_template(db: Session, new_template: PaymentTermsTemplateCreate):
    if not new_template.lines:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Payment Terms Template must at least contain one line")
    
    total = Decimal("0.00")
    prepared_lines: list[dict] = []

    for line in new_template.lines:
        if line.invoice_portions <= Decimal("0.00"):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Invoice Portions must be greather than 0.00")
        term = repository.get_payment_term_by_id(db, line.payment_term_id)
        if term is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Payment Term ID is not found")
        if not term.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Payment Term ID is inactive")

        total = total + line.invoice_portions
        prepared_lines.append(
            {
                "payment_term_id": line.payment_term_id,
                "invoice_portions": line.invoice_portions,
                "description": line.description
            }
        )

    if total != Decimal("100.00"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Invoice Portions must sum to 100.00%")

    new_data = {
        "template_name": new_template.template_name,
        "is_active": True
    }
    return repository.create_payment_term_template(db, new_data, prepared_lines)

def update_payment_term_template(db: Session, template_id: int, update_template: PaymentTermsTemplateUpdate):
    template = repository.get_payment_terms_template_by_id(db, template_id)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Template ID is not found")
    if not template.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Template can not be updated because it is inactive")

    update_data = update_template.model_dump(exclude_unset=True)
    new_lines_data = update_data.pop("lines", None)

    validated_lines: list[dict] = []
    if new_lines_data is not None:
        if not new_lines_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Payment Terms Template must at least contain one line")

        total = Decimal("0.00")
        for line_data in new_lines_data:
            payment_term_id = line_data.get("payment_term_id")
            invoice_portions = line_data.get("invoice_portions")

            if payment_term_id is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Payment Term ID is required for each template line")
            if invoice_portions is None or Decimal(str(invoice_portions)) <= Decimal("0.00"):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invoice portion must be greater than 0.00")

            payment_term = repository.get_payment_term_by_id(db, payment_term_id)
            if payment_term is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Payment Term ID is not found")
            if not payment_term.is_active:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Payment Term ID is inactive")

            portion_decimal = Decimal(str(invoice_portions))
            total = total + portion_decimal
            validated_lines.append(
                {
                    "payment_term_id": payment_term_id,
                    "invoice_portions": portion_decimal,
                    "description": line_data.get("description"),
                }
            )

        if total != Decimal("100.00"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invoice portions must sum to exactly 100.00%")

    for key, value in update_data.items():
        setattr(template, key, value)

    if new_lines_data is not None:
        template.lines.clear()
        db.flush()
        for line_data in validated_lines:
            template.lines.append(PaymentTermsTemplateLine(**line_data))

    return repository.update_payment_term_template(db, template)

def activate_payment_term(db: Session, term_id: int, activate: Activation):
    term = repository.get_payment_term_by_id(db, term_id)
    if term is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Payment Term ID is not found")

    if activate.is_active is not None:
        term.is_active = activate.is_active

    return repository.activate_payment_term(db, term)

def activate_payment_term_template(db: Session, template_id: int, activate: Activation):
    template = repository.get_payment_terms_template_by_id(db, template_id)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Payment Term Template ID is not found")

    if activate.is_active is not None:
        template.is_active = activate.is_active

    return repository.activate_payment_term_template(db, template)
