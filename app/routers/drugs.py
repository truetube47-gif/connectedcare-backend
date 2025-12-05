from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models.drug import Drug

router = APIRouter()

@router.get("/drugs")
def get_all_drugs(db: Session = Depends(get_session)):
    return db.exec(select(Drug)).all()

@router.get("/drugs/search")
def search_drugs(query: str, db: Session = Depends(get_session)):
    statement = select(Drug).where(Drug.trade_name.ilike(f"%{query}%"))
    return db.exec(statement).all()
