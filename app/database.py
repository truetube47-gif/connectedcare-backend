from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)

def init_db():
    from app.models import user, patient, physician, pharmacy, prescription, document, links, chat
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session