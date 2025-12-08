import os
import uuid
from typing import Optional
from fastapi import UploadFile
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class UploadService:
    def __init__(self):
        self.upload_dir = "uploads"
        self.base_url = settings.BASE_URL or "https://connectedcare-backend-production.up.railway.app"
        
        # Create upload directories
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(os.path.join(self.upload_dir, "verification_docs"), exist_ok=True)
        os.makedirs(os.path.join(self.upload_dir, "profile_pictures"), exist_ok=True)
        os.makedirs(os.path.join(self.upload_dir, "prescriptions"), exist_ok=True)
    
    async def upload_file(self, file: UploadFile, folder: str = "general") -> str:
        """Upload a file and return its URL"""
        try:
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Create folder if it doesn't exist
            target_folder = os.path.join(self.upload_dir, folder)
            os.makedirs(target_folder, exist_ok=True)
            
            # Save file
            file_path = os.path.join(target_folder, unique_filename)
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Return URL
            relative_path = os.path.join(folder, unique_filename).replace("\\", "/")
            file_url = f"{self.base_url}/media/{relative_path}"
            
            logger.info(f"File uploaded successfully: {file_url}")
            return file_url
            
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise e
    
    def delete_file(self, file_url: str) -> bool:
        """Delete a file by its URL"""
        try:
            # Extract relative path from URL
            if "/media/" in file_url:
                relative_path = file_url.split("/media/")[-1]
                file_path = os.path.join(self.upload_dir, relative_path)
                
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"File deleted: {file_path}")
                    return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False

# Singleton instance
upload_service = UploadService()

# Export the main function for easy import
async def upload_file(file: UploadFile, folder: str = "general") -> str:
    """Convenience function to upload a file"""
    return await upload_service.upload_file(file, folder)
