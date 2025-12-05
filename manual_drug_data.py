from app.database import engine
from sqlmodel import SQLModel, Session
from app.models.drug import Drug  # Import directly from drug module

# Create tables if not created
SQLModel.metadata.create_all(bind=engine)

# Sample drug data based on the image you showed
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
