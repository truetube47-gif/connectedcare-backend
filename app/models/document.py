from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import JSON
from enum import Enum


class DocumentType(str, Enum):
    PRESCRIPTION = "prescription"
    LAB_REPORT = "lab_report"
    RADIOLOGY_IMAGE = "radiology_image"
    MEDICAL_RECORD = "medical_record"
    INSURANCE_CARD = "insurance_card"
    ID_PROOF = "id_proof"
    OTHER = "other"


class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"
    ARCHIVED = "archived"


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    patient_id: int = Field(foreign_key="patient.id", index=True)
    uploaded_by: Optional[int] = Field(foreign_key="user.id", index=True)

    # File Information
    original_filename: str
    stored_filename: str
    file_path: str
    file_size: int  # in bytes
    mime_type: str

    # Document Metadata
    title: Optional[str] = None
    description: Optional[str] = None
    doc_type: DocumentType = Field(default=DocumentType.OTHER)
    status: DocumentStatus = Field(default=DocumentStatus.UPLOADED)

    # Processing Information
    ocr_text: Optional[str] = None

    # ❌ FIX: "metadata" cannot be used as Python attribute → rename to "meta"
    #     but map it to DB column "metadata" for compatibility
    meta: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSON),           # actual column name
        description="Additional metadata extracted from the document"
    )

    # Security and Access
    is_encrypted: bool = False

    access_control: List[Dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column("access_control", JSON),
        description="List of users/roles with access to this document"
    )

    # Timestamps
    document_date: Optional[datetime] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None

    # Relationships
    patient: Optional["Patient"] = Relationship(back_populates="documents")
    uploaded_by_user: Optional["User"] = Relationship()

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": 1,
                "uploaded_by": 2,
                "original_filename": "lab_results_2023.pdf",
                "stored_filename": "doc_abc123xyz.pdf",
                "file_path": "/uploads/documents/2023/11/doc_abc123xyz.pdf",
                "file_size": 102400,
                "mime_type": "application/pdf",
                "title": "Blood Test Results - Nov 2023",
                "description": "Complete blood count and lipid profile",
                "doc_type": "lab_report",
                "status": "processed",
                "document_date": "2023-11-20T00:00:00",
                "meta": {
                    "lab_name": "City Lab Diagnostics",
                    "test_type": ["CBC", "Lipid Profile"],
                    "doctor_name": "Dr. Smith"
                }
            }
        }
