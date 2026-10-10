from pydantic import BaseModel
from app.users.schemas import UserResponse

class CustomerUpdate(BaseModel):
    customer_category: str | None = None
    trade_name: str | None = None
    tin: str | None = None
    vat: str | None = None
    sales_tax_id: str | None = None
    certificate_number: str | None = None
    tax_exemption_status: str | None = None

class CustomerDetailResponse(BaseModel):
    id: int
    customer_category: str
    trade_name: str
    tin: str
    vat: str
    sales_tax_id: str
    certificate_number: str
    tax_exemption_status: str

    class Config:
        from_attributes = True

class CustomerUserResponse(BaseModel):
    user: UserResponse
    customer_profile: CustomerDetailResponse | None = None

    class Config:
        from_attributes = True