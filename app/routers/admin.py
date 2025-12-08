import sys
import os
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette import status
from app.database import init_db

# Add the project root to the Python path to allow importing from the root-level script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# from import_drugs import import_drug_data  # Temporarily commented out

router = APIRouter(prefix="/admin", tags=["Admin"])

# --- Simple API Key Security ---
# In a real app, this key MUST be loaded from an environment variable
# e.g., ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY")
ADMIN_API_KEY = "G3EQPXAt_MrDoZWkMcQu-E1pB4HG341cggwETlvvVlA" 
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Dependency to verify the admin API key."""
    if not api_key or api_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Admin API Key"
        )
    return api_key


@router.post("/init-db", dependencies=[Depends(verify_api_key)])
def initialize_database():
    """Initializes the database and creates all tables."""
    init_db()
    return {"status": "ok", "message": "Database tables created"}

 @router.post("/import-drugs", dependencies=[Depends(verify_api_key)])
 async def trigger_drug_import():
     """
     Triggers the one-time import of drug data from the drugs.xlsx file.
     This is an idempotent operation; it will skip if drugs are already present.
     """
     result = import_drug_data()
     if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
             detail=result["message"]
        )
     return result
