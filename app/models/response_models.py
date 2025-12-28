from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ChatResponse(BaseModel):
    response: str

class OrderStatusResponse(BaseModel):
    status: str
    items: list


class RecommendationResponse(BaseModel):
    products: list


class CartItem(BaseModel):
    product_id: int
    quantity: int
    product_name: str
    price: float

class CartResponse(BaseModel):
    items: List[CartItem]
    total_price: float

class CheckoutResponse(BaseModel):
    order_id: str
    status: str
    items: List[CartItem]
    total_price: float


class PaymentMethodResponse(BaseModel):
    id: int
    last4: str
    brand: str
    exp_month: int
    exp_year: int
    is_default: bool

class TransactionResponse(BaseModel):
    id: int
    amount: float
    currency: str
    status: str
    order_id: str
    created_at: datetime