import pandas as pd
from app.database import engine, init_db
from app.models import Drug
from sqlmodel import SQLModel, Session
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_drug_data():
    """
    Reads drug data from an Excel sheet and populates the database.
    This function is designed to be idempotent by checking if drugs already exist.
    """
    try:
        logger.info("Starting drug data import process...")
        
        # Ensure database and tables are created
        init_db()
        
        # Load the excel file
        try:
            df = pd.read_excel("drugs.xlsx", engine='openpyxl')
            logger.info(f"Successfully loaded Excel file with {len(df)} rows.")
        except Exception as e:
            logger.error(f"Error reading Excel file: {e}", exc_info=True)
            return {"status": "error", "message": f"Failed to read drugs.xlsx: {e}"}

        with Session(engine) as session:
            # Optional: Check if the table is already populated to avoid duplication
            existing_drug_count = session.query(Drug).count()
            if existing_drug_count > 0:
                message = f"Drug table is already populated with {existing_drug_count} records. Skipping import."
                logger.info(message)
                return {"status": "skipped", "message": message}

            logger.info("Importing new drug data into the database...")
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
        
        final_count = session.query(Drug).count()
        success_message = f"Successfully imported {final_count} drugs."
        logger.info(success_message)
        return {"status": "success", "message": success_message}

    except Exception as e:
        logger.error(f"An unexpected error occurred during drug import: {e}", exc_info=True)
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}

# This allows the script to be run directly from the command line
if __name__ == "__main__":
    result = import_drug_data()
    print(result)
