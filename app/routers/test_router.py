from fastapi import APIRouter, Depends
from sqlmodel import Session, select, create_engine, SQLModel, Field
from typing import Optional
from pydantic import BaseModel

# Define Drug model here to avoid import issues
class Drug(SQLModel, table=True):
    __tablename__ = "drugs"
    __table_args__ = {"extend_existing": True}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    trade_name: str = Field(nullable=False)
    price: Optional[str] = Field(default=None)
    strength: Optional[str] = Field(default=None)
    dosage_form: Optional[str] = Field(default=None)
    manufacturer: Optional[str] = Field(default=None)
    pack_size: Optional[str] = Field(default=None)
    composition: Optional[str] = Field(default=None)

# Pydantic model for response
class DrugRead(BaseModel):
    id: int
    trade_name: str
    price: Optional[str] = None
    strength: Optional[str] = None
    dosage_form: Optional[str] = None
    manufacturer: Optional[str] = None
    pack_size: Optional[str] = None
    composition: Optional[str] = None

    class Config:
        from_attributes = True

router = APIRouter()

# Create a simple engine for this router
engine = create_engine("sqlite:///./app.db")

def get_session():
    with Session(engine) as session:
        yield session

@router.get("/test/drugs")
async def test_drugs():
    return [
        {"id": 1, "name": "Test Drug 1"},
        {"id": 2, "name": "Test Drug 2"}
    ]

@router.get("/api/drugs")
def get_drugs_api():
    print("DEBUG: api/drugs endpoint called")
    return [
        {"id": 1, "trade_name": "Test Drug 1", "strength": "10mg"},
        {"id": 2, "trade_name": "Test Drug 2", "strength": "20mg"}
    ]

@router.get("/drugs", response_model=list[DrugRead])
def get_all_drugs(session: Session = Depends(get_session)):
    print("DEBUG: get_all_drugs endpoint called")
    try:
        drugs = session.exec(select(Drug)).all()
        print(f"DEBUG: Found {len(drugs)} drugs")
        return drugs
    except Exception as e:
        print(f"DEBUG: Error in get_all_drugs: {e}")
        return []

@router.get("/drugs/search", response_model=list[DrugRead])
def search_drugs(query: str, session: Session = Depends(get_session)):
    statement = select(Drug).where(Drug.trade_name.ilike(f"%{query}%"))
    drugs = session.exec(statement).all()
    return drugs
