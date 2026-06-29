from pydantic import BaseModel, Field
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str

    
class ChatRequest(BaseModel):
    message: str

class OrderStatusRequest(BaseModel):
    order_id: str

class RecommendationRequest(BaseModel):
    user_id: str


class AddToCartRequest(BaseModel):
    product_id: int
    quantity: int = 1

class RemoveFromCartRequest(BaseModel):
    product_id: int
    quantity: Optional[int] = None  

class UpdateCartRequest(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)

class ViewCartRequest(BaseModel):
    user_id: str

class CheckoutRequest(BaseModel):
    payment_method_id: Optional[int] = None
    card_number: Optional[str] = None
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    cvc: Optional[str] = None
    save_card: bool = False


class PaymentMethodCreate(BaseModel):
    card_number: str
    exp_month: int
    exp_year: int
    cvc: str

class PaymentRequest(BaseModel):
    amount: float
    currency: str = "USD"
    payment_method_id: Optional[int] = None
    save_card: bool = False


class UpdateLocationRequest(BaseModel):
    tracking_number: str
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)