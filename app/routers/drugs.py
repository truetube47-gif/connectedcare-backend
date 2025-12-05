from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models.drug import Drug

router = APIRouter(prefix="/drugs", tags=["Drugs"])

# --------------------------

# Get all drugs

# --------------------------

@router.get("/")
def get_all_drugs(db: Session = Depends(get_session)):
drugs = db.exec(select(Drug)).all()
return drugs

# --------------------------

# Get drug by ID

# --------------------------

@router.get("/{drug_id}")
def get_drug_by_id(drug_id: int, db: Session = Depends(get_session)):
drug = db.get(Drug, drug_id)
if not drug:
raise HTTPException(status_code=404, detail="Drug not found")
return drug

# --------------------------

# Search drugs by trade_name

# --------------------------

@router.get("/search")
def search_drugs(query: str, db: Session = Depends(get_session)):
statement = select(Drug).where(Drug.trade_name.ilike(f"%{query}%"))
results = db.exec(statement).all()
return results

# --------------------------

# Get all unique categories (dosage forms)

# --------------------------

@router.get("/categories")
def get_dosage_categories(db: Session = Depends(get_session)):
statement = select(Drug.dosage_form).distinct()
categories = [row[0] for row in db.exec(statement).all() if row[0] is not None]
return categories
