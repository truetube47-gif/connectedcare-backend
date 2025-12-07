from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from pydantic import BaseModel
from app.database import init_db, get_session
from app.models.user import User, UserRole
from app.utils.security import verify_password, get_password_hash, create_access_token

router = APIRouter()

class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    phone: str | None = None
    role: UserRole = UserRole.PATIENT

@router.post("/register")
def register_user(register_data: RegisterRequest, session: Session = Depends(get_session)):
    try:
        user_exists = session.exec(select(User).where(User.email == register_data.email)).first()
        if user_exists:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        full_name = f"{register_data.first_name} {register_data.last_name}"
        hashed_pw = get_password_hash(register_data.password)
        user = User(
            email=register_data.email, 
            hashed_password=hashed_pw, 
            full_name=full_name, 
            role=register_data.role
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return {"id": user.id, "email": user.email}
    except Exception as e:
        print(f"Error in register_user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    try:
        user = session.exec(select(User).where(User.email == form_data.username)).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token({"sub": str(user.id), "role": user.role.value})
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        print(f"Error in login: {e}")
        raise HTTPException(status_code=500, detail=str(e))