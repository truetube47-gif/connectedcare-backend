from fastapi import APIRouter, UploadFile, File, Depends
from sqlmodel import Session
from app.models.document import Document
from app.database import get_session
from app.utils.file_utils import save_upload

router = APIRouter()

@router.post("/upload/")
def upload_document(patient_id: int, file: UploadFile = File(...), session: Session = Depends(get_session)):
    filepath = save_upload(file.file.read(), file.filename)
    doc = Document(patient_id=patient_id, filename=file.filename, filepath=filepath)
    session.add(doc)
    session.commit()
    session.refresh(doc)
    return doc

@router.get("/")
def list_documents(session: Session = Depends(get_session)):
    from sqlmodel import select
    return session.exec(select(Document)).all()