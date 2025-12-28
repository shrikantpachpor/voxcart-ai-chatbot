from sqlalchemy import Column, Integer, String, text
from app.core.database import Base, engine, SessionLocal
from fastapi import FastAPI, Depends, APIRouter
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

class DummyModel(Base):
    __tablename__ = 'test_model'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("/create-test/")
def create_test(name: str, db: Session = Depends(get_db)):
    new_test = DummyModel(name=name)
    db.add(new_test)
    db.commit()
    db.refresh(new_test)
    return new_test

@router.get("/get-tests/")
def get_tests(db: Session = Depends(get_db)):
    tests = db.query(DummyModel).all()
    return tests

def test_db_connection():
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1
    finally:
        db.close()