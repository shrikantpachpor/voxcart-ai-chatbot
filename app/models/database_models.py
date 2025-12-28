from sqlalchemy import Column, ForeignKey, Integer, String, JSON, DateTime, Boolean, Float, Index
from sqlalchemy.sql import func
from app.core.database import Base
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import JSONB

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=True)
    attributes = Column(JSON, nullable=True)
    image = Column(String, nullable=True)

    carts = relationship("Cart", back_populates="product")


class UserInteraction(Base):
    __tablename__ = "user_interactions"
    id = Column(Integer, primary_key=True)
    session_id = Column(String)
    user_message = Column(String)
    bot_response = Column(String)
    intent = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow())


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    preferences = Column(JSON)

     
class OrderHistory(Base):
    __tablename__ = "order_history"
    __table_args__ = (
        Index('ix_order_history_user_id_order_id', 'user_id', 'order_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True) 
    order_id = Column(String, unique=True)
    order_details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="order_history")

@validates('order_details')
def validate_order_details(self, key, value):
    required_keys = ['items', 'total_price', 'tracking_numbers']
    if not all(k in value for k in required_keys):
        raise ValueError(f"Order details must contain {required_keys}")
    return value

class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    session_id = Column(String)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    product = relationship("Product", back_populates="carts")

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    card_token = Column(String, unique=True)
    last4 = Column(String(4))
    brand = Column(String(20))
    exp_month = Column(Integer)
    exp_year = Column(Integer)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="payment_methods")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    currency = Column(String(3), default="USD")
    status = Column(String(20))
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"))
    order_id = Column(String)
    gateway_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")
    payment_method = relationship("PaymentMethod")
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    payment_methods = relationship(
        "PaymentMethod", 
        order_by="PaymentMethod.id", 
        back_populates="user"
    )
    transactions = relationship(
        "Transaction", 
        order_by="Transaction.id", 
        back_populates="user"
    )
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    orders = relationship(
        "OrderTracking", 
        back_populates="user",
        foreign_keys="OrderTracking.user_id"
    )
    order_history = relationship("OrderHistory", back_populates="user")

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    phone_number = Column(String)
    loyalty_points = Column(Integer, default=0)
    purchase_history = Column(JSON)
    search_history = Column(JSON)
    saved_addresses = Column(JSON)
    medical_conditions = Column(JSON)
    
    user = relationship("User", back_populates="profile")


class ConversationState(BaseModel):
    current_product: Optional[Dict] = None
    pending_action: Optional[str] = None
    required_attributes: Dict[str, str] = {}
    conversation_history: List[Dict] = []
    cart_items: List[Dict] = []
    product_details: Optional[Dict] = None
    search_results: List[Dict] = []
    checkout_stage: Optional[str] = None
    temp_checkout_data: Dict[str, Any] = {}
    selected_address: Optional[Dict] = None
    coupon_code: Optional[str] = None
    payment_method_choice: Optional[str] = None

class OrderTracking(Base):
    __tablename__ = "order_tracking"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    carrier = Column(String)
    carrier_api_key = Column(String)
    tracking_numbers = Column(JSONB)
    delivery_instructions = Column(String)
    geolocation_history = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="orders")

    @validates('tracking_numbers', 'geolocation_history')
    def validate_json_fields(self, key, value):
        if not isinstance(value, list):
            raise ValueError(f"{key} must be a list")
        return value