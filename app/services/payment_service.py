# app/services/payment_service.py - New service file

from datetime import datetime
import random
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.database_models import PaymentMethod, Transaction
from app.core.database import SessionLocal

class PaymentService:
    def __init__(self):
        self.mock_gateway_url = "https://mock-payment-gateway.com"
        
    def _mock_gateway_charge(self, amount: float, token: str) -> dict:
        """Simulate payment gateway response"""
        # Simple mock logic - succeed if even cents amount
        success = int(amount * 100) % 2 == 0
        return {
            "id": f"mock_ch_{random.randint(100000,999999)}",
            "status": "succeeded" if success else "failed",
            "amount": amount,
            "currency": "USD"
        }

    def add_payment_method(self, db: Session, user_id: int, data: dict) -> PaymentMethod:
        """Store mock payment method with tokenization"""
        if not all(key in data for key in ['card_number', 'exp_month', 'exp_year', 'cvc']):
            raise HTTPException(
                status_code=400,
                detail="Missing required card details"
            )
            
        # In real system, this would call payment gateway tokenization API
        token = f"mock_tok_{random.randint(100000,999999)}"
        
        payment_method = PaymentMethod(
            user_id=user_id,
            card_token=token,
            last4=data['card_number'][-4:],
            brand=self._detect_card_type(data['card_number']),
            exp_month=data['exp_month'],
            exp_year=data['exp_year']
        )
        
        db.add(payment_method)
        db.commit()
        db.refresh(payment_method)
        return payment_method
    
    def get_payment_methods(self, db: Session, user_id: int) -> list[PaymentMethod]:
        return db.query(PaymentMethod).filter(
            PaymentMethod.user_id == user_id
        ).order_by(PaymentMethod.created_at.desc()).all()

    def process_payment(self, db: Session, user_id: int, payment_data: dict) -> Transaction:
        """Process payment through mock gateway"""
        user_id = str(user_id)
        # Handle new payment method
        if not payment_data.get('payment_method_id'):
            if not all([
                payment_data.get('card_number'),
                payment_data.get('exp_month'),
                payment_data.get('exp_year'),
                payment_data.get('cvc')
            ]):
                raise HTTPException(
                    status_code=400,
                    detail="Missing required card details for new payment method"
                )
                
            method = self.add_payment_method(db, user_id, {
                'card_number': payment_data['card_number'],
                'exp_month': payment_data['exp_month'],
                'exp_year': payment_data['exp_year']
            })
            
            if payment_data.get('save_card', False):
                # In real system, store the payment method
                pass
        else:
            # Use existing payment method
            method = db.query(PaymentMethod).filter(
                PaymentMethod.id == payment_data['payment_method_id'],
                PaymentMethod.user_id == user_id
            ).first()
            if not method:
                raise HTTPException(status_code=404, detail="Payment method not found")
            
        # Process through mock gateway
        result = self._mock_gateway_charge(
            payment_data['amount'],
            method.card_token
        )
        
        # Create transaction record
        transaction = Transaction(
            user_id=str(user_id),
            amount=payment_data['amount'],
            currency=payment_data['currency'],
            status=result['status'],
            payment_method_id=method.id,
            gateway_id=result['id'],
            order_id=f"ORD_{datetime.now().timestamp()}"
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction



    def get_transaction_history(self, db: Session, user_id: int) -> list[Transaction]:
        return db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).order_by(Transaction.created_at.desc()).all()

    def _detect_card_type(self, number: str) -> str:
        """Simple card brand detection"""
        if number.startswith('4'): return 'visa'
        if 51 <= int(number[:2]) <= 55: return 'mastercard'
        if number.startswith('34') or number.startswith('37'): return 'amex'
        return 'unknown'