from fastapi import APIRouter, HTTPException
from app.core.database import SessionLocal
from app.models.database_models import UserInteraction

router = APIRouter()

@router.get("/logs")
def get_logs():
    db = SessionLocal()
    try:
        logs = db.query(UserInteraction).all()
        return logs
    finally:
        db.close()