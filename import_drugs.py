import pandas as pd
from app.database import engine
from app.models import Drug
from sqlmodel import SQLModel, Session

# Create tables if not created
SQLModel.metadata.create_all(bind=engine)

try:
    df = pd.read_excel("drugs.xlsx", engine='openpyxl')
    print(f"Successfully loaded Excel file with {len(df)} rows")
    print("Columns:", df.columns.tolist())
except Exception as e:
    print(f"Error reading Excel file: {e}")
    # Try reading as CSV if Excel fails
    try:
        df = pd.read_csv("drugs.xlsx")
        print(f"Successfully loaded as CSV with {len(df)} rows")
    except Exception as e2:
        print(f"Error reading as CSV: {e2}")
        exit(1)

with Session(engine) as session:
    for _, row in df.iterrows():
        drug = Drug(
            trade_name=row.get("Trade Name"),
            price=row.get("Price"),
            strength=row.get("Strength"),
            dosage_form=row.get("Dosage Form"),
            manufacturer=row.get("Manufacturer"),
            pack_size=row.get("Pack Size"),
            composition=row.get("Composition"),
        )
        session.add(drug)
    
    session.commit()

print("Drugs imported successfully!")
