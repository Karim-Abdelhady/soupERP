from database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, Numeric
from decimal import Decimal
from typing import List

class PaymentTerm(Base):
    __tablename__ = "paymentterms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    due_days: Mapped[int] = mapped_column(default = 0, nullable=False)
    is_active: Mapped[bool] = mapped_column(default = True, nullable=False)

class PaymentTermsTemplate(Base): #header
    __tablename__ = "paymenttermstemplate"

    id: Mapped[int] = mapped_column(primary_key=True)
    template_name: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(default = True, nullable=False)

    lines: Mapped[List["PaymentTermsTemplateLine"]] = relationship("PaymentTermsTemplateLine", back_populates="template", cascade="all, delete-orphan")

class PaymentTermsTemplateLine(Base):
    __tablename__ = "paymenttermstemplateline"

    id: Mapped[int] = mapped_column(primary_key=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("paymenttermstemplate.id"), nullable=False)
    payment_term_id: Mapped[int] = mapped_column(ForeignKey("paymentterms.id"), nullable=False)
    invoice_portions: Mapped[Decimal] = mapped_column(Numeric(12,2), nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)

    template: Mapped["PaymentTermsTemplate"] = relationship("PaymentTermsTemplate", back_populates="lines")
    payment_term: Mapped["PaymentTerm"] = relationship("PaymentTerm")
