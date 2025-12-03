from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models.pharmacy import Pharmacy
from app.models.prescription import Prescription
from app.models.user import User
from app.database import get_session
from app.utils.security import get_current_active_user

router = APIRouter()

@router.post("/")
def create_pharmacy(pharmacy: Pharmacy, session: Session = Depends(get_session)):
    session.add(pharmacy)
    session.commit()
    session.refresh(pharmacy)
    return pharmacy

@router.get("/")
def list_pharmacies(session: Session = Depends(get_session)):
    return session.exec(select(Pharmacy)).all()

@router.get("/me/prescriptions")
def get_pharmacy_prescriptions(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get all prescriptions assigned to the current pharmacist's pharmacy"""
    if current_user.role != "pharmacy" or current_user.pharmacy is None:
        raise HTTPException(status_code=403, detail="Only pharmacists can access this endpoint")
    
    pharmacy_id = current_user.pharmacy.id
    
    # Get all prescriptions for this pharmacy
    prescriptions = session.exec(
        select(Prescription).where(Prescription.pharmacy_id == pharmacy_id)
    ).all()
    
    return prescriptions