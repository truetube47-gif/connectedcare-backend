from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.database import init_db, get_session
from app.models.user import User, UserRole
from app.utils.security import verify_password, get_password_hash, create_access_token

router = APIRouter()

@router.post("/register")
def register_user(email: str, password: str, full_name: str, role: UserRole, session: Session = Depends(get_session)):
    user_exists = session.exec(select(User).where(User.email == email)).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = get_password_hash(password)
    user = User(email=email, hashed_password=hashed_pw, full_name=full_name, role=role)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"id": user.id, "email": user.email}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}