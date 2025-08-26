import os
import uuid
import firebase_admin
from firebase_admin import credentials, storage
from fastapi import UploadFile
from dotenv import load_dotenv
import tempfile

load_dotenv()

# Initialize Firebase with credentials
try:
    # Path to Firebase service account JSON file
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    
    if not firebase_admin._apps:
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET")
            })
        else:
            # For local development/testing without credentials
            firebase_admin.initialize_app()
    
    # Get bucket reference
    bucket = storage.bucket()
except Exception as e:
    print(f"Firebase initialization error: {e}")
    # This allows the app to run even if Firebase isn't properly configured yet
    bucket = None

class FirebaseStorageService:
    @staticmethod
    async def upload_image(file: UploadFile, folder: str = "questions") -> str:
        """
        Upload image to Firebase Storage
        
        Args:
            file: The image file to upload
            folder: The folder path in Firebase Storage
            
        Returns:
            URL of the uploaded image
        """
        if not bucket:
            raise ValueError("Firebase Storage not initialized")
        
        # Create a unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Full path in Firebase Storage
        file_path = f"{folder}/{unique_filename}"
        
        # Save the file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Read the file content
            content = await file.read()
            # Write to temporary file
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Upload to Firebase Storage
            blob = bucket.blob(file_path)
            blob.upload_from_filename(temp_file_path)
            
            # Make the file publicly accessible
            blob.make_public()
            
            # Remove temporary file
            os.unlink(temp_file_path)
            
            # Return public URL
            return blob.public_url
        except Exception as e:
            # Clean up temporary file in case of error
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise e
    
    @staticmethod
    def delete_image(image_url: str) -> bool:
        """
        Delete an image from Firebase Storage
        
        Args:
            image_url: The public URL of the image to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        if not bucket or not image_url:
            return False
        
        try:
            # Extract blob path from URL
            # URL format: https://storage.googleapis.com/BUCKET_NAME/PATH
            parts = image_url.split('/')
            bucket_idx = parts.index(bucket.name)
            if bucket_idx >= 0 and len(parts) > bucket_idx + 1:
                blob_path = '/'.join(parts[bucket_idx + 1:])
                blob = bucket.blob(blob_path)
                if blob.exists():
                    blob.delete()
                    return True
            return False
        except Exception as e:
            print(f"Error deleting image: {e}")
            return False