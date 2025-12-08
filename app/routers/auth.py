from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr
from app.database import init_db, get_session
from app.models.user import User, UserRole, UserStatus
from app.models.verification import EmailVerification
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.services.email_service import email_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    phone: str | None = None
    role: UserRole = UserRole.PATIENT

@router.post("/register")
async def register_user(register_data: RegisterRequest, session: Session = Depends(get_session)):
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
            phone=register_data.phone,
            role=register_data.role,
            status=UserStatus.PENDING,  # Start as pending until email verified
            is_email_verified=False
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Create and send email verification
        verification = EmailVerification.generate_token(register_data.email)
        session.add(verification)
        session.commit()
        
        # Send verification email (async)
        try:
            await email_service.send_verification_email(register_data.email, verification.token)
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
            # Don't fail registration if email fails
        
        # Return full user info
        user_response = {
            "id": user.id,
            "email": user.email,
            "name": user.full_name,
            "first_name": register_data.first_name,
            "last_name": register_data.last_name,
            "phone": register_data.phone,
            "is_verified": user.is_email_verified,
            "status": user.status,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
            "age": None,
            "specialty": None,
            "role": user.role
        }
        
        return {
            "message": "Registration successful. Please check your email to verify your account.",
            "user": user_response
        }
    except Exception as e:
        logger.error(f"Error in register_user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify-email")
async def verify_email(token: str, session: Session = Depends(get_session)):
    """Verify email using token sent to user"""
    try:
        # Find verification token
        verification = session.exec(
            select(EmailVerification).where(
                EmailVerification.token == token,
                EmailVerification.is_used == False
            )
        ).first()
        
        if not verification:
            raise HTTPException(status_code=400, detail="Invalid or expired verification token")
        
        # Check if token is expired
        from datetime import datetime
        if datetime.utcnow() > verification.expires_at:
            raise HTTPException(status_code=400, detail="Verification token has expired")
        
        # Find user and update verification status
        user = session.exec(select(User).where(User.email == verification.email)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.is_email_verified = True
        user.status = UserStatus.ACTIVE  # Activate user after email verification
        
        # Mark token as used
        verification.is_used = True
        
        session.commit()
        
        return {"message": "Email verified successfully. You can now login to your account."}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in verify_email: {e}")
        raise HTTPException(status_code=500, detail="Email verification failed")

@router.post("/resend-verification")
async def resend_verification(email: str, session: Session = Depends(get_session)):
    """Resend verification email"""
    try:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.is_email_verified:
            raise HTTPException(status_code=400, detail="Email is already verified")
        
        # Create new verification token
        verification = EmailVerification.generate_token(email)
        session.add(verification)
        session.commit()
        
        # Send verification email
        await email_service.send_verification_email(email, verification.token)
        
        return {"message": "Verification email sent successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in resend_verification: {e}")
        raise HTTPException(status_code=500, detail="Failed to resend verification email")

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    try:
        user = session.exec(select(User).where(User.email == form_data.username)).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check if email is verified
        if not user.is_email_verified:
            raise HTTPException(
                status_code=403, 
                detail="Please verify your email before logging in. Check your inbox for the verification email."
            )
        
        # Check if user is active
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=403,
                detail=f"Account is {user.status}. Please contact support."
            )
        
        token = create_access_token({"sub": str(user.id), "role": user.role.value})
        
        # Return user info in response
        name_parts = user.full_name.split(" ", 1)
        first_name = name_parts[0] if len(name_parts) > 0 else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        user_response = {
            "id": user.id,
            "email": user.email,
            "name": user.full_name,
            "first_name": first_name,
            "last_name": last_name,
            "phone": user.phone_number,
            "is_verified": user.is_email_verified,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
            "age": None,
            "specialty": None,
            "role": user.role.value
        }
        
        return {"access_token": token, "token_type": "bearer", "user": user_response}
    except Exception as e:
        print(f"Error in login: {e}")
        raise HTTPException(status_code=500, detail=str(e))