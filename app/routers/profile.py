from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select, SQLModel
from typing import List, Optional
from datetime import datetime
from app.database import get_session
from app.models.user import User, UserRole
from app.models.profile import UserProfile, ProfileVerification, VerificationStatus
from app.utils.security import get_current_user
from app.services.upload_service import upload_file
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ProfileUpdate(SQLModel):
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    license_number: Optional[str] = None
    license_expiry: Optional[str] = None
    specialization: Optional[str] = None
    years_of_experience: Optional[int] = None
    workplace: Optional[str] = None
    workplace_address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    current_medications: Optional[str] = None
    blood_type: Optional[str] = None

@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """Get current user's profile"""
    profile = session.exec(select(UserProfile).where(UserProfile.user_id == current_user.id)).first()
    
    if not profile:
        # Create empty profile
        profile = UserProfile(user_id=current_user.id)
        session.add(profile)
        session.commit()
        session.refresh(profile)
    
    return profile

@router.put("/profile")
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update user profile"""
    profile = session.exec(select(UserProfile).where(UserProfile.user_id == current_user.id)).first()
    
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        session.add(profile)
    
    # Update profile fields
    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(profile, field, value)
    
    # Check if profile is complete (basic fields filled)
    required_fields = ['date_of_birth', 'gender', 'address', 'city']
    is_complete = all(getattr(profile, field) for field in required_fields)
    
    # For professionals, require additional fields
    if current_user.role in [UserRole.PHYSICIAN, UserRole.PHARMACY]:
        professional_fields = ['license_number', 'specialization', 'workplace']
        is_complete = is_complete and all(getattr(profile, field) for field in professional_fields)
    
    profile.is_complete = is_complete
    session.commit()
    
    return {"message": "Profile updated successfully", "is_complete": is_complete}

@router.post("/upload-verification-document")
async def upload_verification_document(
    document_type: str = Form(...),
    document_number: Optional[str] = Form(None),
    issuing_authority: Optional[str] = Form(None),
    issue_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Upload verification document for professional accounts"""
    
    # Only physicians and pharmacists can upload verification documents
    if current_user.role not in [UserRole.PHYSICIAN, UserRole.PHARMACY]:
        raise HTTPException(status_code=403, detail="Only professionals can upload verification documents")
    
    # Validate document type
    allowed_types = {
        UserRole.PHYSICIAN: ["professional_id", "medical_license", "degree_certificate"],
        UserRole.PHARMACY: ["professional_id", "pharmacy_license", "degree_certificate"]
    }
    
    if document_type not in allowed_types[current_user.role]:
        raise HTTPException(status_code=400, detail=f"Invalid document type for {current_user.role}")
    
    # Upload file
    try:
        file_url = await upload_file(file, folder="verification_docs")
    except Exception as e:
        logger.error(f"Failed to upload verification document: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload document")
    
    # Create verification record
    verification = ProfileVerification(
        user_id=current_user.id,
        document_type=document_type,
        document_url=file_url,
        document_number=document_number,
        issuing_authority=issuing_authority,
        issue_date=datetime.fromisoformat(issue_date) if issue_date else None,
        expiry_date=datetime.fromisoformat(expiry_date) if expiry_date else None
    )
    
    session.add(verification)
    
    # Update user profile verification status
    profile = session.exec(select(UserProfile).where(UserProfile.user_id == current_user.id)).first()
    if profile:
        profile.verification_status = VerificationStatus.PENDING
    
    session.commit()
    
    return {"message": "Document uploaded successfully", "document_url": file_url}

@router.get("/verification-documents")
async def get_verification_documents(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get user's verification documents"""
    documents = session.exec(
        select(ProfileVerification).where(ProfileVerification.user_id == current_user.id)
    ).all()
    
    return documents

@router.get("/pending-approvals")
async def get_pending_approvals(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get pending professional approvals (admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    pending = session.exec(
        select(ProfileVerification)
        .where(ProfileVerification.status == VerificationStatus.PENDING)
        .order_by(ProfileVerification.created_at)
    ).all()
    
    return pending

@router.post("/approve-verification/{verification_id}")
async def approve_verification(
    verification_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Approve verification document (admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    verification = session.exec(
        select(ProfileVerification).where(ProfileVerification.id == verification_id)
    ).first()
    
    if not verification:
        raise HTTPException(status_code=404, detail="Verification document not found")
    
    verification.status = VerificationStatus.APPROVED
    verification.reviewed_by = current_user.id
    verification.reviewed_at = datetime.utcnow()
    
    # Update user profile
    profile = session.exec(select(UserProfile).where(UserProfile.user_id == verification.user_id)).first()
    if profile:
        # Check if all required documents are approved
        all_verifications = session.exec(
            select(ProfileVerification).where(ProfileVerification.user_id == verification.user_id)
        ).all()
        
        required_docs = 3  # Number of required documents
        approved_docs = sum(1 for v in all_verifications if v.status == VerificationStatus.APPROVED)
        
        if approved_docs >= required_docs:
            profile.verification_status = VerificationStatus.APPROVED
            # Activate user if email is also verified
            user = session.exec(select(User).where(User.id == verification.user_id)).first()
            if user and user.is_email_verified:
                user.status = "active"
    
    session.commit()
    
    return {"message": "Verification approved successfully"}

@router.post("/reject-verification/{verification_id}")
async def reject_verification(
    verification_id: int,
    rejection_reason: str = Form(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Reject verification document (admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    verification = session.exec(
        select(ProfileVerification).where(ProfileVerification.id == verification_id)
    ).first()
    
    if not verification:
        raise HTTPException(status_code=404, detail="Verification document not found")
    
    verification.status = VerificationStatus.REJECTED
    verification.rejection_reason = rejection_reason
    verification.reviewed_by = current_user.id
    verification.reviewed_at = datetime.utcnow()
    
    # Update user profile
    profile = session.exec(select(UserProfile).where(UserProfile.user_id == verification.user_id)).first()
    if profile:
        profile.verification_status = VerificationStatus.REJECTED
    
    session.commit()
    
    return {"message": "Verification rejected successfully"}
