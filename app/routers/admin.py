from fastapi import APIRouter
from app.database import init_db

router = APIRouter()

@router.post("/admin/init-db")
def initialize_database():
    init_db()
    return {"status": "ok", "message": "Database tables created"}
