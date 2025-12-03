from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.models.prescription import Prescription
from app.database import get_session

router = APIRouter()

@router.post("/")
def create_prescription(prescription: Prescription, session: Session = Depends(get_session)):
    session.add(prescription)
    session.commit()
    session.refresh(prescription)
    return prescription

@router.get("/")
def list_prescriptions(session: Session = Depends(get_session)):
    return session.exec(select(Prescription)).all()