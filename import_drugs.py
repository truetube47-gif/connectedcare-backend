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
            return {"status": "error", "message": f"Failed to read drugs.xlsx: {e}. The Excel file appears to be corrupted or empty. Please provide a valid Excel file with drug data."}

        with Session(engine) as session:
            # Optional: Check if the table is already populated to avoid duplication
            existing_drug_count = session.query(Drug).count()
            if existing_drug_count > 0:
                message = f"Drug table is already populated with {existing_drug_count} records. Skipping import."
                logger.info(message)
                return {"status": "skipped", "message": message}

            logger.info("Importing new drug data into the database...")
            
            # Map Excel columns to database fields
            drugs_to_import = []
            for _, row in df.iterrows():
                drug_data = {
                    "trade_name": str(row.get("trade_name", "")).strip(),
                    "generic_name": str(row.get("generic_name", "")).strip(),
                    "strength": str(row.get("strength", "")).strip() if pd.notna(row.get("strength")) else None,
                    "dosage_form": str(row.get("dosage_form", "")).strip() if pd.notna(row.get("dosage_form")) else None,
                    "manufacturer": str(row.get("manufacturer", "")).strip() if pd.notna(row.get("manufacturer")) else None,
                    "ndc": str(row.get("package_size", "")).strip() if pd.notna(row.get("package_size")) else None
                }
                
                # Only add if we have at least trade_name and generic_name
                if drug_data["trade_name"] and drug_data["generic_name"]:
                    drugs_to_import.append(Drug(**drug_data))
            
            if not drugs_to_import:
                return {"status": "error", "message": "No valid drug data found in Excel file"}
            
            # Bulk insert
            session.add_all(drugs_to_import)
            session.commit()
            
            logger.info(f"Successfully imported {len(drugs_to_import)} drugs.")
            return {"status": "success", "message": f"Successfully imported {len(drugs_to_import)} drugs"}

    except Exception as e:
        logger.error(f"An unexpected error occurred during drug import: {e}", exc_info=True)
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}

# By removing the __main__ block, this script can no longer be executed directly.
# The import_drug_data function must now be called explicitly from another part
# of the application, such as the admin API endpoint.
