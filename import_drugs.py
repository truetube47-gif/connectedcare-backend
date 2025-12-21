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
        
        # Drop and recreate the drugs table to handle schema changes
        from app.models.drug import Drug
        Drug.__table__.drop(engine, checkfirst=True)
        Drug.__table__.create(engine, checkfirst=True)
        logger.info("Dropped and recreated drugs table with new schema")
        
        # Load the excel file
        try:
            # Try openpyxl first
            df = pd.read_excel("drugs.xlsx", engine='openpyxl')
            logger.info(f"Successfully loaded Excel file with {len(df)} rows.")
            logger.info(f"Columns found: {list(df.columns)}")
        except Exception as e1:
            logger.error(f"openpyxl failed: {e1}")
            try:
                # Try xlrd as fallback
                df = pd.read_excel("drugs.xlsx", engine='xlrd')
                logger.info(f"Successfully loaded Excel file with xlrd - {len(df)} rows.")
            except Exception as e2:
                logger.error(f"xlrd failed: {e2}")
                try:
                    # Try default engine
                    df = pd.read_excel("drugs.xlsx")
                    logger.info(f"Successfully loaded Excel file with default engine - {len(df)} rows.")
                except Exception as e3:
                    logger.error(f"All engines failed: {e3}")
                    return {"status": "error", "message": f"Failed to read drugs.xlsx with all engines: {e3}"}

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
                    "medicine_name": str(row.get("Medicine_Name", "")).strip(),
                    "commercial_name": str(row.get("Commercial_Name", "")).strip() if pd.notna(row.get("Commercial_Name")) else None,
                    "scientific_name": str(row.get("Scientific_Name", "")).strip() if pd.notna(row.get("Scientific_Name")) else None,
                    "company": str(row.get("Company", "")).strip() if pd.notna(row.get("Company")) else None,
                    "description": str(row.get("Description", "")).strip() if pd.notna(row.get("Description")) else None
                }
                
                # Only add if we have at least medicine_name
                if drug_data["medicine_name"]:
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
