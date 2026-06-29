from fastapi import APIRouter, Depends, Request, Response, HTTPException
from uuid import uuid4
from datetime import timedelta
import logging

from app.models.request_models import (
    ChatRequest, OrderStatusRequest, RecommendationRequest, 
    AddToCartRequest, RemoveFromCartRequest, UpdateCartRequest, CheckoutRequest, 
    LoginRequest, UpdateLocationRequest
)
from app.models.response_models import ChatResponse
from app.services.chat_service import ChatService
from app.services.ecommerce_service import EcommerceService
from app.services.payment_service import PaymentService
from app.services.profile_service import ProfileService
from app.services.order_service import OrderService
from app.models.database_models import User, UserCreate
from app.core.security import rate_limit_check, create_access_token, get_password_hash, verify_password, get_current_user
from app.core.database import SessionLocal
from app.core.logging import logger


router = APIRouter()


@router.post("/add-to-cart")
async def add_to_cart(request: AddToCartRequest, current_user: User = Depends(get_current_user)):
    ecom_service = EcommerceService()
    db = SessionLocal()
    try:
        return ecom_service.add_to_cart(
            db=db, 
            user_id=str(current_user.id), 
            session_id=str(current_user.id), 
            product_id=request.product_id, 
            quantity=request.quantity
        )
    finally:
        db.close()


@router.post("/remove-from-cart")
async def direct_remove_from_cart(
    request: RemoveFromCartRequest,
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        result = EcommerceService().remove_from_cart(
            user_id=str(current_user.id),
            product_id=request.product_id,
            quantity=request.quantity
        )
        return result
    finally:
        db.close()

@router.post("/update-cart")
async def update_cart(
    request: UpdateCartRequest,
    current_user: User = Depends(get_current_user),
):
    db = SessionLocal()
    try:
        return EcommerceService().update_cart_quantity(
            db=db,
            user_id=str(current_user.id),
            product_id=request.product_id,
            quantity=request.quantity,
        )
    finally:
        db.close()

@router.post("/view-cart")
async def view_cart(request: Request, current_user: User = Depends(get_current_user)):
    data = await request.json()
    response_format = data.get("response_format", "text")
    chat_service = ChatService()
    return chat_service.view_cart_api(
        current_user, 
        session_id=str(current_user.id),  
        response_format=response_format
    )

@router.post("/checkout")
async def checkout(request: CheckoutRequest, current_user: User = Depends(get_current_user)):
    chat_service = ChatService()
    db = SessionLocal()
    try:
        cart = chat_service.ecom_service.view_cart(db, current_user.id, "")
        if not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        if not request.payment_method_id and not all([
            request.card_number,
            request.exp_month,
            request.exp_year,
            request.cvc
        ]):
            raise HTTPException(
                status_code=400,
                detail="Either provide saved payment method or new card details"
            )
        
        payment_service = PaymentService()
        transaction = payment_service.process_payment(
            db=db,
            user_id=str(current_user.id),
            payment_data={
                "amount": cart.total_price,
                "currency": "USD",
                "payment_method_id": request.payment_method_id,
                "card_number": request.card_number,
                "exp_month": request.exp_month,
                "exp_year": request.exp_year,
                "cvc": request.cvc,
                "save_card": request.save_card
            }
        )
        
        if transaction.status != "succeeded":
            raise HTTPException(status_code=400, detail=f"Payment failed: {transaction.status}")
        
        checkout_result = chat_service.ecom_service.checkout(db, current_user.id, "")
        return {
            "order_id": checkout_result.order_id,
            "transaction_id": transaction.id,
            "amount": transaction.amount,
            "status": "completed"
        }
    finally:
        db.close()

@router.post("/")
async def chat_endpoint(request: ChatRequest, client: Request, response: Response, current_user: User = Depends(get_current_user)):
    session_id = client.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid4())
        response.set_cookie(key="session_id", value=session_id, httponly=True, max_age=315360000, expires=315360000)

    rate_limit_check(client)
    user_message = request.message.strip()

    if not user_message:
        logger.error(f"Empty message received from IP: {client.client.host}")
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    try:
        chat_service = ChatService()
        return chat_service.generate_response(
            user_message=user_message,
            session_id=session_id,
            current_user=current_user
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")

@router.post("/confirm-payment")
async def confirm_payment(transaction_id: str, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        payment_service = PaymentService()
        transaction = payment_service.get_transaction(db, transaction_id)
        
        if transaction.user_id != current_user.id:
            raise HTTPException(403, "Invalid transaction")
            
        if transaction.status == "succeeded":
            ecom_service = EcommerceService()
            order = ecom_service.checkout(db, current_user.id, "")
            
            return {
                "status": "completed",
                "order_id": order.order_id,
                "items": order.items
            }
        
        return {"status": transaction.status}
    finally:
        db.close()


@router.post("/ask")
async def ask_question(request: ChatRequest, client: Request, response: Response, current_user = Depends(get_current_user)):
    session_id = client.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid4())
        response.set_cookie(key="session_id", value=session_id, httponly=True)

    rate_limit_check(client)
    user_message = request.message.strip()

    if not user_message:
        logger.error(f"Empty message received from IP: {client.client.host}")
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    chat_service = ChatService()
    return chat_service.generate_response(
        user_message=user_message,
        session_id=session_id,
        current_user=current_user
    )

@router.post("/order-status")
async def get_order_status(request: OrderStatusRequest, client: Request, current_user: User = Depends(get_current_user)):
    rate_limit_check(client)
    order_id = request.order_id.strip()

    if not order_id:
        logging.error(f"Empty order_id received from IP: {client.client.host}")
        raise HTTPException(status_code=400, detail="Order ID cannot be empty.")
    
    ecom_service = EcommerceService()
    return ecom_service.get_order_status(order_id)

@router.post("/recommendations")
async def get_recommendations(request: RecommendationRequest, client: Request, current_user: User = Depends(get_current_user)):
    rate_limit_check(client)
    user_id = request.user_id.strip()

    if not user_id:
        logging.error(f"Empty user_id received from IP: {client.client.host}")
        raise HTTPException(status_code=400, detail="User ID cannot be empty.")
    
    chat_service = ChatService()
    return chat_service.get_recommendations(user_id)

@router.post("/register")
async def register(user: UserCreate):
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = get_password_hash(user.password)
        new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        profile_service = ProfileService()
        profile_service._get_or_create_profile(db, new_user.id)

        return {"message": "User registered successfully"}
    finally:
        db.close()

@router.post("/login")
async def login(login_data: LoginRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(days=365*10))
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/profile")
async def get_full_profile(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        profile_data = ProfileService().get_full_profile(db, current_user.id)
        return {
            "response": f"Here's your profile: {profile_data}",
            "profile": profile_data
        }
    finally:
        db.close()

@router.post("/update-address")
async def update_address(
    address: dict, 
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        profile = ProfileService()._get_or_create_profile(db, current_user.id)
        addresses = profile.saved_addresses or []
        addresses.append(address)
        
        profile.saved_addresses = addresses
        db.commit()
        
        return {"response": "Address updated successfully!"}
    finally:
        db.close()

@router.post("/init-profile")
async def init_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        service = ProfileService()
        profile = service._get_or_create_profile(db, current_user.id)
        
        if 'phone' in profile_data:
            profile.phone_number = profile_data['phone']
        if 'address' in profile_data:
            profile.saved_addresses.append(profile_data['address'])
            
        db.commit()
        return {"message": "Profile initialized successfully"}
    finally:
        db.close()

@router.post("/track-order")
async def track_order(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        order = OrderService().get_shipment_details(db, current_user.id)
        
        if not order:
            return {
                "error": "No orders found",
                "message": "You haven't placed any orders yet!",
                "details":{}
            }
            
        return {
            "tracking": order.tracking_numbers,
            "instructions": order.delivery_instructions,
            "locations": order.geolocation_history
        }
    except Exception as e:
        logger.error(f"Tracking error: {str(e)}")
        return HTTPException(500, "Could not retrieve tracking info.")
    finally:
        db.close()

@router.post("/update-location")
async def update_shipment_location(
    location: UpdateLocationRequest,
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        OrderService().update_location(
            db, 
            location.tracking_number,
            location.lat,
            location.lng
        )
        return {"message": "Location updated"}
    except ValueError as e:
        raise HTTPException(422, str(e))
    finally:
        db.close()