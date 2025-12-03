import json
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel
import os
import sys

# Add the app's root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.medicine import Medicine
from app.config import settings

def ingest_medicines():
    # Path to your JSON file
    json_file_path = 'medicines.json' # Place this file in the 'backend' directory

    if not os.path.exists(json_file_path):
        print(f"Error: {json_file_path} not found. Please place your JSON file in the backend directory.")
        return

    with open(json_file_path, 'r', encoding='utf-8') as f:
        medicines_data = json.load(f)

    engine = create_engine(settings.DATABASE_URL)

    # This will drop and recreate the Medicine table each time the script is run
    # Be careful if you have other data you want to keep
    SQLModel.metadata.drop_all(engine, tables=[Medicine.__table__])
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        count = 0
        for med_data in medicines_data:
            # Map your JSON fields to the Medicine model fields
            # This is an example, you MUST adjust it to match your JSON structure
            medicine = Medicine(
                name=med_data.get('name'),
                generic_name=med_data.get('genericName'),
                brand_name=med_data.get('brandName'),
                manufacturer=med_data.get('manufacturer'),
                dosage_form=med_data.get('dosageForm'),
                strength=med_data.get('strength'),
                description=med_data.get('description')
            )
            session.add(medicine)
            count += 1
        
        session.commit()
        print(f"Successfully ingested {count} medicines into the database.")

if __name__ == "__main__":
    ingest_medicines()
