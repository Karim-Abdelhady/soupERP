from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from app.purchasing.payment_terms.models import PaymentTerm, PaymentTermsTemplate, PaymentTermsTemplateLine

def get_payment_terms(db: Session):
    statement = select(PaymentTerm)
    return db.scalars(statement).all()

def get_payment_term_by_id(db: Session, term_id: int):
    statement = select(PaymentTerm).where(PaymentTerm.id == term_id)
    return db.scalar(statement)

def create_payment_term(db: Session, new_term: PaymentTerm):
    new_data = PaymentTerm(**new_term)
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return new_data

def update_payment_term(db: Session, update_term: PaymentTerm):
    db.commit()
    db.refresh(update_term)
    return update_term

def get_payment_terms_templates(db: Session):
    statement = (
        select(PaymentTermsTemplate)
        .options(selectinload(PaymentTermsTemplate.lines))
    )
    return db.scalars(statement).all()

def get_payment_terms_template_by_id(db: Session, template_id: int):
    statement = (
        select(PaymentTermsTemplate)
        .options(selectinload((PaymentTermsTemplate.lines)))
        .where(PaymentTermsTemplate.id == template_id)
    )
    return db.scalar(statement)

def create_payment_term_template(db: Session, new_template: PaymentTermsTemplate, lines: list[dict]):
    new_data = PaymentTermsTemplate(**new_template)
    for line in lines:
        new_data.lines.append(PaymentTermsTemplateLine(**line))
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return new_data

def update_payment_term_template(db: Session, update_template: PaymentTermsTemplate, lines: list[dict]):
    if lines is not None:
        update_template.lines.clear()
        db.flush()
        for line in lines:
            update_template.lines.append(PaymentTermsTemplateLine(**line))
    db.commit()
    db.refresh(update_template)
    return update_template

def activate_payment_term(db: Session, activation: PaymentTerm):
    db.commit()
    db.refresh(activation)
    return activation

def activate_payment_term_template(db: Session, activation: PaymentTermsTemplate):
    db.commit()
    db.refresh(activation)
    return activation