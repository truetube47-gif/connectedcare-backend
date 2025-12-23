from sqlalchemy import Column, Integer, String, Text
from sqlmodel import SQLModel, Field

class Drug(SQLModel, table=True):
    __tablename__ = "drugs"
    
    id: int | None = Field(default=None, primary_key=True)
    trade_name: str = Field(nullable=False)
    price: str | None = Field(default=None)
    strength: str | None = Field(default=None)
    dosage_form: str | None = Field(default=None)
    manufacturer: str | None = Field(default=None)
    pack_size: str | None = Field(default=None)
    composition: str | None = Field(default=None)

    # Compatibility properties for the app
    @property
    def medicine_name(self):
        return self.trade_name
    
    @property
    def commercial_name(self):
        return self.trade_name  # Use trade_name as commercial_name
    
    @property
    def scientific_name(self):
        return self.composition  # Use composition as scientific_name
    
    @property
    def company(self):
        return self.manufacturer

    def __repr__(self):
        return f"<Drug(id={self.id}, trade_name='{self.trade_name}')>"
