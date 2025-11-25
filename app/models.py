from pydantic import BaseModel
from typing import List

class Order(BaseModel):
    customer_name: str
    items: List[str]
    total_amount: float
