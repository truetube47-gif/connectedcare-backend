from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models.drug import Drug

router = APIRouter(tags=["Drugs"])

# --------------------------

# Get all drugs

# --------------------------

@router.get("/")
def get_all_drugs(db: Session = Depends(get_session)):
    # Get actual drugs from database
    drugs = db.exec(select(Drug)).all()
    if not drugs:
        # If no drugs in database, return sample data
        return [
            {"id": 1, "medicine_name": "Abilify 10 mg", "commercial_name": "Abilify", "scientific_name": "Aripiprazole"},
            {"id": 2, "medicine_name": "Abilify 15 mg", "commercial_name": "Abilify", "scientific_name": "Aripiprazole"}
        ]
    return drugs

# --------------------------

# Get drug by ID

# --------------------------

@router.get("/search")
def search_drugs(query: str, db: Session = Depends(get_session)):
    # Search actual drugs from database
    statement = select(Drug).where(Drug.medicine_name.ilike(f"%{query}%"))
    results = db.exec(statement).all()
    
    if not results:
        # If no drugs found in database, search sample data
        all_drugs = [
            {"id": 1, "medicine_name": "Abilify 10 mg", "commercial_name": "Abilify", "scientific_name": "Aripiprazole"},
            {"id": 2, "medicine_name": "Abilify 15 mg", "commercial_name": "Abilify", "scientific_name": "Aripiprazole"}
        ]
        filtered_drugs = [drug for drug in all_drugs if query.lower() in drug["medicine_name"].lower()]
        return filtered_drugs
    
    return results

@router.get("/item/{drug_id}")
def get_drug_by_id(drug_id: int, db: Session = Depends(get_session)):
    drug = db.get(Drug, drug_id)
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    return drug

# --------------------------

# Get all unique categories (dosage forms)

# --------------------------

@router.get("/categories")
def get_dosage_categories(db: Session = Depends(get_session)):
    statement = select(Drug.commercial_name).distinct()
    categories = [row[0] for row in db.exec(statement).all() if row[0] is not None]
    return categories
