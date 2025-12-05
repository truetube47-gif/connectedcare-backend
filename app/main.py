from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_db

from app.routers import (
    auth,
    patients,
    physicians,
    pharmacies,
    prescriptions,
    documents,
    connections,
    uploads,
    chat,
    admin,
    drugs,   # only ONCE
)

app = FastAPI(title="ConnectedCare Backend")

# Serve uploaded media
app.mount("/media", StaticFiles(directory="uploads"), name="media")

# Initialize DB
@app.on_event("startup")
def on_startup():
    init_db()

# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(patients.router, prefix="/patients", tags=["patients"])
app.include_router(physicians.router, prefix="/physicians", tags=["physicians"])
app.include_router(pharmacies.router, prefix="/pharmacies", tags=["pharmacies"])
app.include_router(prescriptions.router, prefix="/prescriptions", tags=["prescriptions"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(connections.router, prefix="/connections", tags=["connections"])
app.include_router(uploads.router)
app.include_router(chat.router)
app.include_router(admin.router)

# Drugs router (NO prefix → gives clean `/drugs`, `/drugs/search`, etc.)
app.include_router(drugs.router, tags=["drugs"])

@app.get("/")
async def root():
    return {"status": "ConnectedCare backend running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "connectedcare-backend"}
