from pydantic import BaseModel
from app.users.schemas import UserResponse

class SupplierUpdate(BaseModel):
    supplier_category: str | None = None
    tax_id: str | None = None
    ein: str | None = None
    vat: str | None = None
    diversity_status: str | None = None
    vendor_tier: str | None = None


class SupplierDetailResponse(BaseModel):
    id: int
    supplier_category: str
    tax_id: str | None = None
    ein: str | None = None
    vat: str | None = None
    diversity_status: str | None = None
    vendor_tier: str | None = None

    class Config:
        from_attributes = True

class UserSupplierResponse(BaseModel):
    user: UserResponse
    supplier_profile: SupplierDetailResponse | None = None

    class Config:
        from_attributes = True        

