from sqlmodel import SQLModel, Field, Session, create_engine
from typing import Optional

# Define a simple Drug model without importing from app.models
class Drug(SQLModel, table=True):
    __tablename__ = "drugs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    trade_name: str = Field(nullable=False)
    price: Optional[str] = Field(default=None)
    strength: Optional[str] = Field(default=None)
    dosage_form: Optional[str] = Field(default=None)
    manufacturer: Optional[str] = Field(default=None)
    pack_size: Optional[str] = Field(default=None)
    composition: Optional[str] = Field(default=None)

# Sample drug data
sample_drugs = [
    {
        "trade_name": "Abilify 10 mg 10",
        "price": None,
        "strength": "10 mg",
        "dosage_form": "Tablets",
        "manufacturer": "Otsuka Pharmaceuti",
        "pack_size": "10 Tablets",
        "composition": "Aripiprazole"
    },
    {
        "trade_name": "Abilify 15 mg 10",
        "price": None,
        "strength": "15 mg",
        "dosage_form": "Tablets",
        "manufacturer": "Otsuka Pharmaceuti",
        "pack_size": "10 Tablets",
        "composition": "Aripiprazole"
    },
    {
        "trade_name": "Abilify 20 mg 10",
        "price": None,
        "strength": "20 mg",
        "dosage_form": "Tablets",
        "manufacturer": "Otsuka Pharmaceuti",
        "pack_size": "10 Tablets",
        "composition": "Aripiprazole"
    },
    {
        "trade_name": "Abilify 30 mg 10",
        "price": None,
        "strength": "30 mg",
        "dosage_form": "Tablets",
        "manufacturer": "Otsuka Pharmaceuti",
        "pack_size": "10 Tablets",
        "composition": "Aripiprazole"
    },
    {
        "trade_name": "Abilify 5 mg 10",
        "price": None,
        "strength": "5 mg",
        "dosage_form": "Tablets",
        "manufacturer": "Otsuka Pharmaceuti",
        "pack_size": "10 Tablets",
        "composition": "Aripiprazole"
    }
]

# Create engine and import data
engine = create_engine("sqlite:///./app.db")  # Using SQLite for simplicity
SQLModel.metadata.create_all(bind=engine)

with Session(engine) as session:
    for drug_data in sample_drugs:
        drug = Drug(**drug_data)
        session.add(drug)
    
    session.commit()
    print(f"Successfully imported {len(sample_drugs)} sample drugs!")

# Test the import
with Session(engine) as session:
    count = session.query(Drug).count()
    print(f"Total drugs in database: {count}")
    
    # Show first few drugs
    drugs = session.query(Drug).limit(3).all()
    for drug in drugs:
        print(f"- {drug.trade_name} ({drug.strength}) - {drug.manufacturer}")
