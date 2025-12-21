from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.models.medicine import Medicine
from app.database import get_session

router = APIRouter(prefix="/medicines", tags=["Medicines"])

@router.get("/search", response_model=List[Medicine])
def search_medicines(
    query: str,
    session: Session = Depends(get_session)
):
    """
    Search for medicines by name, commercial name, or scientific name.
    """
    search_term = f"%{query.lower()}%"
    
    statement = select(Medicine).where(
        (Medicine.medicine_name.ilike(search_term)) |
        (Medicine.commercial_name.ilike(search_term)) |
        (Medicine.scientific_name.ilike(search_term))
    ).limit(50)
    
    results = session.exec(statement).all()
    return results
