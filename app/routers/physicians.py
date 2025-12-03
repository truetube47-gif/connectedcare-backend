from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.models.physician import Physician
from app.models.patient import Patient
from app.models.links import PatientPhysicianLink
from app.models.document import Document
from app.models.user import User
from app.database import get_session
from app.utils.security import get_current_active_user

router = APIRouter(
    prefix="/physicians",
    tags=["physicians"],
)

@router.post("/")
def create_physician(physician: Physician, session: Session = Depends(get_session)):
    session.add(physician)
    session.commit()
    session.refresh(physician)
    return physician

@router.get("/", response_model=List[Physician])
def list_physicians(session: Session = Depends(get_session)):
    """
    Get a list of all physicians.
    In a real app, you'd add pagination and filtering (e.g., by specialty, location).
    """
    physicians = session.exec(select(Physician)).all()
    return physicians

@router.get("/me/patients")
def get_physician_patients(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get all patients linked to the current physician"""
    if current_user.role != "physician" or current_user.physician is None:
        raise HTTPException(status_code=403, detail="Only physicians can access this endpoint")
    
    physician_id = current_user.physician.id
    
    # Get all active links for this physician
    links = session.exec(
        select(PatientPhysicianLink).where(
            PatientPhysicianLink.physician_id == physician_id,
            PatientPhysicianLink.status == "active"
        )
    ).all()
    
    # Get patient details for each link
    patients = []
    for link in links:
        patient = session.exec(select(Patient).where(Patient.id == link.patient_id)).first()
        if patient:
            patients.append({
                "patient": patient,
                "link_status": link.status,
                "linked_at": link.created_at
            })
    
    return patients

@router.get("/patients/{patient_id}/documents")
def get_patient_documents(
    patient_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get documents for a specific patient (only if physician is linked to patient)"""
    if current_user.role != "physician" or current_user.physician is None:
        raise HTTPException(status_code=403, detail="Only physicians can access this endpoint")
    
    physician_id = current_user.physician.id
    
    # Check if link exists and is active
    link = session.exec(
        select(PatientPhysicianLink).where(
            PatientPhysicianLink.physician_id == physician_id,
            PatientPhysicianLink.patient_id == patient_id,
            PatientPhysicianLink.status == "active"
        )
    ).first()
    
    if not link:
        raise HTTPException(status_code=403, detail="You are not authorized to access this patient's documents")
    
    # Get patient documents
    documents = session.exec(
        select(Document).where(Document.patient_id == patient_id)
    ).all()
    
    return documents