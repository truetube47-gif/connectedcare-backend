from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models.patient import Patient
from app.database import get_session

router = APIRouter()

@router.post("/")
def create_patient(patient: Patient, session: Session = Depends(get_session)):
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient

@router.get("/")
def list_patients(session: Session = Depends(get_session)):
    patients = session.exec(select(Patient)).all()
    return patients