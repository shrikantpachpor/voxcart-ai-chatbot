# services/order_service.py
from sqlalchemy.orm import Session
from app.models.database_models import OrderTracking, User
from datetime import datetime
from sqlalchemy import func
from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import JSONB


class OrderService:
    def __init__(self):
        self.carrier_api_url = "https://api.shipping-carrier.com"
        
    def get_shipment_details(self, db: Session, user_id: str):
        


        user_id = str(user_id)
        temp = db.query(OrderTracking)
        temp2 = db.query(OrderTracking).filter(OrderTracking.user_id == user_id)

        order = db.query(OrderTracking).filter(
            OrderTracking.user_id == user_id
        ).first()

        if not order:

            return self._create_demo_tracking(db, user_id)
            

        return order

    def update_location(self, db: Session, tracking_number: str, lat: float, lng: float):
        try:
            order = db.query(OrderTracking).filter(
                OrderTracking.tracking_numbers.contains([tracking_number])
            ).first()
            
            if not order:
                # Create demo tracking for testing
                order = OrderTracking(
                    user_id=user_id,
                    tracking_numbers=[tracking_number],
                    geolocation_history=[]
                )
                db.add(order)
                
            history = order.geolocation_history or []
            history.append({"lat": lat, "lng": lng})
            order.geolocation_history = history
            db.commit()
            return order
            
        except Exception as e:
            db.rollback()
            raise HTTPException(500, f"Location update failed: {str(e)}")


    def get_carrier_credentials(self, db: Session, user_id: str):
        """Do NOT expose raw API keys through API endpoints"""
        order = self.get_shipment_details(db, user_id)
        # Only return non-sensitive carrier info
        return {
            "carrier": order.carrier,
            "status": "tracked"
        }
    
    def _create_demo_tracking(self, db: Session, user_id: int):
        """Create demo tracking for testing - use environment variables for keys"""
        try:
            from decouple import config
            # Get carrier API key from environment, fallback to masked demo key
            carrier_key = config('DEMO_CARRIER_API_KEY', default='*** CONFIGURE IN .env ***')
            
            new_order = OrderTracking(
                user_id=user_id,
                carrier="DEMO",
                carrier_api_key=carrier_key,
                tracking_numbers=["DEMO-123"],
                delivery_instructions="Signature required",
                geolocation_history=[]
            )
            db.add(new_order)
            db.commit()
            return new_order
        except Exception as e:
            db.rollback()
            return None
