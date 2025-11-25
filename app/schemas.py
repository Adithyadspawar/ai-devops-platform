# app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List

class OrderBase(BaseModel):
    customer_name: str = Field(..., example="Alice")
    items: List[str] = Field(..., example=["margherita", "coke"])
    total_amount: float = Field(..., example=12.5)

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[str] = Field(None, example="delivered")
    items: Optional[List[str]] = None
    total_amount: Optional[float] = None

class OrderInDB(OrderBase):
    id: int
    status: str
    created_at: str

    class Config:
        orm_mode = True
