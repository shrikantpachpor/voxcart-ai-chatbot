# app/services/profile_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.database_models import UserProfile

class ProfileService:
    def get_full_profile(self, db: Session, user_id: int):
        user_id = str(user_id)
        """Vulnerable method exposing all PII"""


        profile = db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()

        if not profile:
            raise HTTPException(404, "Profile not found")
            
        return {
            "phone": profile.phone_number,
            "points": profile.loyalty_points,
            "purchases": profile.purchase_history,
            "searches": profile.search_history,
            "addresses": profile.saved_addresses,
            "medical": profile.medical_conditions  # Critical vulnerability
        }

    def update_search_history(self, db: Session, user_id: int, query: str):
        """Unsanitized search history tracking"""
        profile = self._get_or_create_profile(db, user_id)
        
        searches = profile.search_history or []
        searches.append(query)  # No input sanitization
        profile.search_history = searches[-50:]  # Keep last 50
        
        db.commit()
        return profile


    def _get_or_create_profile(self, db: Session, user_id: int):
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()
        
        if not profile:
            profile = UserProfile(
                user_id=user_id,
                phone_number="",
                loyalty_points=100,  # Initial bonus points
                purchase_history={"items": [], "total_spent": 0},
                search_history=[],
                saved_addresses=[],
                medical_conditions=[]
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
            
        return profile
