from typing import Optional
from sqlmodel import SQLModel, Field

class Medicine(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    medicine_name: str = Field(index=True)
    commercial_name: Optional[str] = Field(index=True)
    scientific_name: Optional[str] = Field(index=True)
    company: Optional[str]
    description: Optional[str]