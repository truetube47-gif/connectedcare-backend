import os
import logging
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Email configuration - using environment variables
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", ""),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", ""),
    MAIL_FROM=os.getenv("MAIL_FROM", "noreply@connectedcare.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS=bool(os.getenv("MAIL_STARTTLS", True)),
    MAIL_SSL_TLS=bool(os.getenv("MAIL_SSL_TLS", False)),
    USE_CREDENTIALS=bool(os.getenv("USE_CREDENTIALS", True)),
    VALIDATE_CERTS=bool(os.getenv("VALIDATE_CERTS", True)),
    TEMPLATE_FOLDER= os.path.join(os.path.dirname(__file__), "..", "templates")
)

class EmailService:
    def __init__(self):
        self.fm = FastMail(conf)
        # Setup Jinja2 environment for templates
        template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    async def send_verification_email(self, email: str, token: str) -> bool:
        """Send email verification email"""
        try:
            # Create verification URL
            verification_url = f"https://connectedcare-app.com/verify-email?token={token}"
            
            # Render template
            template = self.jinja_env.get_template("verification_email.html")
            html_content = template.render(
                verification_url=verification_url,
                email=email
            )
            
            message = MessageSchema(
                subject="Verify your ConnectedCare account",
                recipients=[email],
                body=html_content,
                subtype="html"
            )
            
            await self.fm.send_message(message)
            logger.info(f"Verification email sent to {email}")
            return True
            
        except ConnectionErrors as e:
            logger.error(f"Failed to send verification email to {email}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending verification email: {e}")
            return False
    
    async def send_password_reset_email(self, email: str, token: str) -> bool:
        """Send password reset email"""
        try:
            # Create reset URL
            reset_url = f"https://connectedcare-app.com/reset-password?token={token}"
            
            # Render template
            template = self.jinja_env.get_template("password_reset_email.html")
            html_content = template.render(
                reset_url=reset_url,
                email=email
            )
            
            message = MessageSchema(
                subject="Reset your ConnectedCare password",
                recipients=[email],
                body=html_content,
                subtype="html"
            )
            
            await self.fm.send_message(message)
            logger.info(f"Password reset email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {e}")
            return False
    
    async def send_approval_notification(self, email: str, role: str, approved: bool) -> bool:
        """Send profile approval/rejection notification"""
        try:
            template_name = "profile_approved.html" if approved else "profile_rejected.html"
            template = self.jinja_env.get_template(template_name)
            html_content = template.render(
                email=email,
                role=role,
                approved=approved
            )
            
            subject = f"Your ConnectedCare profile has been {'approved' if approved else 'rejected'}"
            
            message = MessageSchema(
                subject=subject,
                recipients=[email],
                body=html_content,
                subtype="html"
            )
            
            await self.fm.send_message(message)
            logger.info(f"Approval notification sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send approval notification to {email}: {e}")
            return False

# Singleton instance
email_service = EmailService()
