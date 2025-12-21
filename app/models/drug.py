from sqlalchemy import Column, Integer, String, Text
from sqlmodel import SQLModel, Field

class Drug(SQLModel, table=True):
    __tablename__ = "drugs"
    
    id: int | None = Field(default=None, primary_key=True)
    medicine_name: str = Field(nullable=False)
    commercial_name: str | None = Field(default=None)
    scientific_name: str | None = Field(default=None)
    company: str | None = Field(default=None)
    description: str | None = Field(default=None)

    def __repr__(self):
        return f"<Drug(id={self.id}, medicine_name='{self.medicine_name}')>"
