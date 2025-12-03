from datetime import datetime
from sqlmodel import SQLModel, Field

class PatientPhysicianLink(SQLModel, table=True):
    """
    A link table representing the relationship between a Patient and a Physician.
    This establishes the authorization for a physician to view patient data.
    """
    patient_id: int = Field(foreign_key="patient.id", primary_key=True)
    physician_id: int = Field(foreign_key="physician.id", primary_key=True)
    
    # Status of the connection, e.g., 'active', 'pending_approval', 'revoked'
    status: str = Field(default="pending_approval", index=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Note: The Patient-Pharmacist link is handled directly via the `pharmacy_id`
# in the `Prescription` model, so a separate linking table is not strictly necessary
# for the initial prescription workflow.
