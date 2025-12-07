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

router = APIRouter(tags=["physicians"])

@router.post("/")
def create_physician(physician: Physician, session: Session = Depends(get_session)):
    session.add(physician)
    session.commit()
    session.refresh(physician)
    return physician

@router.get("/", response_model=List[dict])
def list_physicians(session: Session = Depends(get_session)):
    """
    Get a list of all physicians.
    Returns mock data for now since no physicians exist in database.
    """
    # Return mock data for testing
    return [
        {
            "id": 1,
            "user_id": 1,
            "medical_license_number": "MD123456",
            "specialty": "Cardiology",
            "sub_specialties": ["Interventional Cardiology", "Heart Failure"],
            "years_of_experience": 10,
            "clinic_name": "Heart Care Clinic",
            "clinic_phone": "+1-555-0123",
            "clinic_email": "heart@clinic.com",
            "clinic_website": "https://heartcare.clinic",
            "address_line1": "123 Medical Dr",
            "address_line2": "Suite 100",
            "city": "New York",
            "state": "NY",
            "postal_code": "10001",
            "country": "United States",
            "is_verified": True,
            "verification_status": "verified",
            "rating": 4.5,
            "review_count": 120,
            "consultation_fee": 150.0,
            "availability": "Mon-Fri 9AM-5PM",
            "is_available": True,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-12-01T00:00:00Z"
        },
        {
            "id": 2,
            "user_id": 2,
            "medical_license_number": "MD789012",
            "specialty": "Pediatrics",
            "sub_specialties": ["Neonatology", "Developmental Pediatrics"],
            "years_of_experience": 8,
            "clinic_name": "Kids Health Center",
            "clinic_phone": "+1-555-0456",
            "clinic_email": "kids@health.com",
            "clinic_website": "https://kidshealth.center",
            "address_line1": "456 Children Ave",
            "address_line2": "Floor 2",
            "city": "Los Angeles",
            "state": "CA",
            "postal_code": "90001",
            "country": "United States",
            "is_verified": True,
            "verification_status": "verified",
            "rating": 4.8,
            "review_count": 95,
            "consultation_fee": 120.0,
            "availability": "Mon-Thu 8AM-6PM",
            "is_available": True,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-12-01T00:00:00Z"
        }
    ]

@router.post("/sample")
def create_sample_physicians(session: Session = Depends(get_session)):
    """Create sample physicians for testing"""
    from app.models.user import User, UserRole
    from app.utils.security import get_password_hash
    
    # Check if physicians already exist
    existing = session.exec(select(Physician)).all()
    if existing:
        return {"message": f"Already have {len(existing)} physicians"}
    
    # Create sample physicians
    sample_physicians = [
        {
            "user_id": None,  # Will be set after creating user
            "license_number": "MD123456",
            "specialty": "Cardiology",
            "clinic_name": "Heart Care Clinic",
            "clinic_address": "123 Medical Dr, City, State",
            "clinic_phone": "+1-555-0123",
            "clinic_email": "heart@clinic.com",
            "years_of_experience": 10,
            "education": "MD from Harvard Medical School",
            "certifications": "Board Certified in Cardiology",
            "availability": "Mon-Fri 9AM-5PM",
            "consultation_fee": 150.00,
            "is_available": True,
            "rating": 4.5,
            "review_count": 120
        },
        {
            "user_id": None,
            "license_number": "MD789012",
            "specialty": "Pediatrics",
            "clinic_name": "Kids Health Center",
            "clinic_address": "456 Children Ave, City, State",
            "clinic_phone": "+1-555-0456",
            "clinic_email": "kids@health.com",
            "years_of_experience": 8,
            "education": "MD from Johns Hopkins",
            "certifications": "Board Certified in Pediatrics",
            "availability": "Mon-Thu 8AM-6PM",
            "consultation_fee": 120.00,
            "is_available": True,
            "rating": 4.8,
            "review_count": 95
        }
    ]
    
    created_physicians = []
    for i, sample in enumerate(sample_physicians, 1):
        # Create user account for physician
        user = User(
            email=f"doctor{i}@test.com",
            hashed_password=get_password_hash("password123"),
            full_name=f"Dr. Test {i}",
            role=UserRole.PHYSICIAN
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Create physician profile
        physician = Physician(
            user_id=user.id,
            **{k: v for k, v in sample.items() if k != "user_id"}
        )
        session.add(physician)
        session.commit()
        session.refresh(physician)
        created_physicians.append(physician)
    
    return {"message": f"Created {len(created_physicians)} sample physicians"}

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