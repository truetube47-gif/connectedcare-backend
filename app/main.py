from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import auth, patients, physicians, pharmacies, prescriptions, documents, connections, uploads, chat
from app.database import init_db

app = FastAPI(title="ConnectedCare Backend")

# Mount a directory to serve static media files (like uploaded chat images)
app.mount("/media", StaticFiles(directory="uploads"), name="media")

# Create DB tables on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Include all the API routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(patients.router, prefix="/patients", tags=["patients"])
app.include_router(physicians.router, prefix="/physicians", tags=["physicians"])
app.include_router(pharmacies.router, prefix="/pharmacies", tags=["pharmacies"])
app.include_router(prescriptions.router, prefix="/prescriptions", tags=["prescriptions"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(connections.router, prefix="/connections", tags=["connections"])
app.include_router(uploads.router) # No prefix needed if defined in the router
app.include_router(chat.router)

@app.get("/")
async def root():
    return {"status": "ConnectedCare backend running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "connectedcare-backend"}