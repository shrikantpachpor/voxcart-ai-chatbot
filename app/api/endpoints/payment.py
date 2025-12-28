from fastapi import APIRouter, Depends, HTTPException
from app.models.request_models import PaymentMethodCreate, PaymentRequest
from app.models.response_models import PaymentMethodResponse, TransactionResponse
from app.models.database_models import User
from app.services.payment_service import PaymentService
from app.core.database import get_db
from app.core.security import get_current_user
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/add-payment-method", response_model=PaymentMethodResponse)
async def add_payment_method(
    data: PaymentMethodCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PaymentService()
    return service.add_payment_method(db, current_user.id, data.dict())


@router.get("/get-payment-methods", response_model=list[PaymentMethodResponse])
async def get_payment_methods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PaymentService()
    return service.get_payment_methods(db, current_user.id)


@router.post("/charge", response_model=TransactionResponse)
async def process_payment(
    payment_data: PaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PaymentService()
    return service.process_payment(db, current_user.id, payment_data.dict())

@router.get("/history", response_model=list[TransactionResponse])
async def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PaymentService()
    return service.get_transaction_history(db, current_user.id)