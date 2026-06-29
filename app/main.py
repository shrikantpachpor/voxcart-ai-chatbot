from fastapi import FastAPI, Depends, HTTPException
import logging
import ujson
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from decouple import config

from app.api.endpoints import chat, health, admin, payment
from app.services import fake_ecommerce_api
from app.core.database import SessionLocal
from app.models.database_models import User, UserCreate
from app.core.security import get_password_hash

# Initialize FastAPI app
app = FastAPI(title="Voxbot API")

# Add CORS middleware FIRST so error responses also include CORS headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in config('ALLOWED_ORIGINS').split(',') if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware after CORS
app.add_middleware(
    SessionMiddleware,
    secret_key=config('SESSION_SECRET_KEY'),
    session_cookie="session_id",
    max_age=315360000
)



log_level = config('LOG_LEVEL', default='INFO').upper()
log_filename = config('LOG_FILENAME')
logging.basicConfig(filename=log_filename, level=getattr(logging, log_level, logging.INFO), format="%(asctime)s - %(levelname)s - %(message)s")

# Include API routes
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(payment.router, prefix="/payment", tags=["Payment"])
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(fake_ecommerce_api.router, prefix="/fake", tags=["Fake Ecommerce API"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])



@app.get("/")
async def home():
    return {"message": "Voxbot API is running!"}

@app.post("/register")
async def register(user: UserCreate):
    """Register a new user"""
    db = SessionLocal()
    try:
        # Check if email is already registered
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash the password before storing
        hashed_password = get_password_hash(user.password)
        
        # Create and store new user
        new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {"message": "User registered successfully"}
    finally:
        db.close()
class UJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: any) -> bytes:
        return ujson.dumps(content).encode("utf-8")


# Use UJSONResponse globally
app.default_response_class = UJSONResponse

