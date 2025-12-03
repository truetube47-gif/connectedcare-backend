"""
Firebase Admin SDK initialization for ConnectCare backend
Handles authentication, Firestore, and Storage for the backend services
"""

import os
from firebase_admin import credentials, firestore, initialize_app, storage
from typing import Optional

class FirebaseAdmin:
    """Singleton class for Firebase Admin SDK initialization"""
    
    _instance: Optional['FirebaseAdmin'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseAdmin, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize_firebase()
            FirebaseAdmin._initialized = True
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK with service account"""
        try:
            # Check if service account file exists
            service_account_path = os.path.join(os.path.dirname(__file__), 'firebase-config.json')
            
            if os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
            else:
                # For development, use environment variables or default credentials
                cred = credentials.ApplicationDefault()
            
            # Initialize Firebase app
            self.app = initialize_app(cred, name='connectcare-backend')
            
            # Initialize Firestore
            self.db = firestore.client(app=self.app)
            
            # Initialize Storage
            self.bucket = storage.bucket(app=self.app)
            
            print("Firebase Admin SDK initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize Firebase Admin SDK: {e}")
            raise
    
    @property
    def firestore(self) -> firestore.Client:
        """Get Firestore client"""
        return self.db
    
    @property
    def storage(self) -> storage.Bucket:
        """Get Storage bucket"""
        return self.bucket
    
    def get_collection(self, collection_name: str) -> firestore.CollectionReference:
        """Get a Firestore collection reference"""
        return self.db.collection(collection_name)
    
    def get_document(self, collection_name: str, document_id: str) -> firestore.DocumentReference:
        """Get a Firestore document reference"""
        return self.db.collection(collection_name).document(document_id)

# Global Firebase admin instance
firebase_admin = FirebaseAdmin()
