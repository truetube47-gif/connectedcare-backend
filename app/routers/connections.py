from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime

from app.database import get_session
from app.models.links import PatientPhysicianLink
from app.models.user import User
from app.utils.security import get_current_active_user

router = APIRouter(prefix="/connections", tags=["Connections"])

@router.post("/link-physician/{physician_id}", status_code=201)
def link_patient_to_physician(
    physician_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Allows a logged-in patient to request a connection with a physician.
    """
    if current_user.role != "patient" or current_user.patient is None:
        raise HTTPException(status_code=403, detail="Only patients can perform this action.")

    patient_id = current_user.patient.id
    
    # Check if link already exists
    existing_link = session.exec(
        select(PatientPhysicianLink).where(
            PatientPhysicianLink.patient_id == patient_id,
            PatientPhysicianLink.physician_id == physician_id
        )
    ).first()
    
    if existing_link:
        raise HTTPException(status_code=400, detail="Connection already exists or is pending.")

    new_link = PatientPhysicianLink(patient_id=patient_id, physician_id=physician_id)
    session.add(new_link)
    session.commit()
    session.refresh(new_link)
    
    return new_link

@router.post("/accept-connection/{patient_id}")
def accept_patient_connection(
    patient_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Allows a physician to accept a patient connection request.
    """
    if current_user.role != "physician" or current_user.physician is None:
        raise HTTPException(status_code=403, detail="Only physicians can perform this action.")

    physician_id = current_user.physician.id

    # Find the pending link
    link = session.exec(
        select(PatientPhysicianLink).where(
            PatientPhysicianLink.patient_id == patient_id,
            PatientPhysicianLink.physician_id == physician_id,
            PatientPhysicianLink.status == "pending_approval"
        )
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="No pending connection request found.")

    # Update link status to active
    link.status = "active"
    link.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(link)

    return {"message": "Connection accepted successfully", "link": link}

@router.post("/reject-connection/{patient_id}")
def reject_patient_connection(
    patient_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Allows a physician to reject a patient connection request.
    """
    if current_user.role != "physician" or current_user.physician is None:
        raise HTTPException(status_code=403, detail="Only physicians can perform this action.")

    physician_id = current_user.physician.id

    # Find the pending link
    link = session.exec(
        select(PatientPhysicianLink).where(
            PatientPhysicianLink.patient_id == patient_id,
            PatientPhysicianLink.physician_id == physician_id,
            PatientPhysicianLink.status == "pending_approval"
        )
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="No pending connection request found.")

    # Update link status to rejected
    link.status = "rejected"
    link.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(link)

    return {"message": "Connection rejected successfully", "link": link}

@router.get("/pending-requests")
def get_pending_connection_requests(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all pending connection requests for the current physician.
    """
    if current_user.role != "physician" or current_user.physician is None:
        raise HTTPException(status_code=403, detail="Only physicians can perform this action.")

    physician_id = current_user.physician.id

    # Get all pending links for this physician
    pending_links = session.exec(
        select(PatientPhysicianLink).where(
            PatientPhysicianLink.physician_id == physician_id,
            PatientPhysicianLink.status == "pending_approval"
        )
    ).all()

    return pending_links
