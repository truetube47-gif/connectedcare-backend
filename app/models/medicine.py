from typing import Optional
from sqlmodel import SQLModel, Field

class Medicine(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    generic_name: Optional[str] = Field(index=True)
    brand_name: Optional[str] = Field(index=True)
    manufacturer: Optional[str]
    dosage_form: Optional[str] # e.g., "Tablet", "Capsule", "Syrup"
    strength: Optional[str] # e.g., "500mg", "10ml"
    description: Optional[str]
    
    # Add any other fields from your Excel sheet here