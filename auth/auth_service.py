"""
Authentication service for ConnectCare backend
Handles user authentication, JWT tokens, and user management
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from firebase_admin import auth
from ..firebase_admin import firebase_admin

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Service for handling authentication operations"""
    
    def __init__(self):
        self.db = firebase_admin.firestore
        self.auth = auth
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None
    
    async def create_user_with_email_and_password(
        self,
        email: str,
        password: str,
        full_name: str,
        user_type: str
    ) -> Dict[str, Any]:
        """Create a new user in Firebase Authentication and Firestore"""
        try:
            # Create user in Firebase Auth
            user = auth.create_user(
                email=email,
                password=password,
                display_name=full_name
            )
            
            # Store additional user data in Firestore
            user_data = {
                "uid": user.uid,
                "email": email,
                "full_name": full_name,
                "user_type": user_type,  # "patient", "physician", "pharmacy"
                "created_at": datetime.utcnow(),
                "is_active": True,
                "email_verified": user.email_verified
            }
            
            # Save to users collection
            firebase_admin.get_collection("users").document(user.uid).set(user_data)
            
            # Create type-specific profile
            if user_type == "patient":
                await self._create_patient_profile(user.uid, user_data)
            elif user_type == "physician":
                await self._create_physician_profile(user.uid, user_data)
            elif user_type == "pharmacy":
                await self._create_pharmacy_profile(user.uid, user_data)
            
            return {
                "success": True,
                "user_id": user.uid,
                "email": user.email,
                "display_name": user.display_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_patient_profile(self, user_id: str, user_data: Dict[str, Any]):
        """Create patient-specific profile"""
        patient_profile = {
            **user_data,
            "date_of_birth": None,
            "phone": None,
            "address": None,
            "emergency_contact": None,
            "medical_history": [],
            "allergies": [],
            "current_medications": []
        }
        firebase_admin.get_collection("patients").document(user_id).set(patient_profile)
    
    async def _create_physician_profile(self, user_id: str, user_data: Dict[str, Any]):
        """Create physician-specific profile"""
        physician_profile = {
            **user_data,
            "specialty": None,
            "license_number": None,
            "years_of_experience": None,
            "clinic_address": None,
            "consultation_fee": None,
            "available_hours": {},
            "rating": 0.0,
            "total_consultations": 0
        }
        firebase_admin.get_collection("physicians").document(user_id).set(physician_profile)
    
    async def _create_pharmacy_profile(self, user_id: str, user_data: Dict[str, Any]):
        """Create pharmacy-specific profile"""
        pharmacy_profile = {
            **user_data,
            "pharmacy_name": user_data["full_name"],
            "license_number": None,
            "address": None,
            "phone": None,
            "email": user_data["email"],
            "operating_hours": {},
            "delivery_available": False,
            "rating": 0.0,
            "verified": False
        }
        firebase_admin.get_collection("pharmacies").document(user_id).set(pharmacy_profile)
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with email and password"""
        try:
            # Note: Firebase Admin SDK doesn't support password authentication directly
            # This would typically be handled on the client side
            # For backend authentication, we verify the ID token from client
            
            return {
                "success": False,
                "error": "Password authentication should be handled on client side"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_id_token(self, id_token: str) -> Dict[str, Any]:
        """Verify Firebase ID token"""
        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            
            # Get user data from Firestore
            user_doc = firebase_admin.get_collection("users").document(uid).get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                return {
                    "success": True,
                    "user": user_data
                }
            else:
                return {
                    "success": False,
                    "error": "User not found in Firestore"
                }
                
        except auth.InvalidIdTokenError:
            return {
                "success": False,
                "error": "Invalid ID token"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_user_profile(self, uid: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile in Firestore"""
        try:
            user_ref = firebase_admin.get_collection("users").document(uid)
            
            # Update user document
            user_ref.update(update_data)
            
            # Update type-specific profile
            user_doc = user_ref.get()
            if user_doc.exists:
                user_type = user_doc.to_dict().get("user_type")
                
                if user_type == "patient":
                    firebase_admin.get_collection("patients").document(uid).update(update_data)
                elif user_type == "physician":
                    firebase_admin.get_collection("physicians").document(uid).update(update_data)
                elif user_type == "pharmacy":
                    firebase_admin.get_collection("pharmacies").document(uid).update(update_data)
            
            return {
                "success": True,
                "message": "Profile updated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_user(self, uid: str) -> Dict[str, Any]:
        """Delete user from Firebase Auth and Firestore"""
        try:
            # Delete from Firebase Auth
            auth.delete_user(uid)
            
            # Delete from Firestore collections
            collections_to_check = ["users", "patients", "physicians", "pharmacies"]
            
            for collection_name in collections_to_check:
                doc_ref = firebase_admin.get_collection(collection_name).document(uid)
                if doc_ref.get().exists:
                    doc_ref.delete()
            
            return {
                "success": True,
                "message": "User deleted successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Global auth service instance
auth_service = AuthService()
