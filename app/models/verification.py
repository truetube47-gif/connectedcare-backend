from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import SQLModel, Field
import secrets

class EmailVerification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, nullable=False)
    token: str = Field(unique=True, index=True)
    expires_at: datetime
    is_used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @classmethod
    def generate_token(cls, email: str) -> 'EmailVerification':
        """Generate a new verification token for email"""
        token = secrets.urlsafe_b64encode(secrets.token_bytes(32)).decode()
        expires_at = datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
        return cls(email=email, token=token, expires_at=expires_at)

class PasswordReset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, nullable=False)
    token: str = Field(unique=True, index=True)
    expires_at: datetime
    is_used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @classmethod
    def generate_token(cls, email: str) -> 'PasswordReset':
        """Generate a new password reset token"""
        token = secrets.urlsafe_b64encode(secrets.token_bytes(32)).decode()
        expires_at = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
        return cls(email=email, token=token, expires_at=expires_at)
