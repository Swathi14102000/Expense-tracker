from pydantic import BaseModel
from typing import Optional

class ExpenseCreate(BaseModel):
    category: str
    amount: float
    description: Optional[str] = None
    payment_mode: Optional[str] = None
    merchant_name: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[str] = None
