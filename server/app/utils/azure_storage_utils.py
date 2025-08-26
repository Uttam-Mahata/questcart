import os
import uuid
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from fastapi import UploadFile
from dotenv import load_dotenv
import tempfile
from typing import Optional

load_dotenv()

class AzureStorageService:
    def __init__(self):
        # Initialize Azure Storage with connection string or account details
        self.account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        self.account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        
        try:
            if self.connection_string:
                self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            elif self.account_name and self.account_key:
                account_url = f"https://{self.account_name}.blob.core.windows.net"
                self.blob_service_client = BlobServiceClient(account_url=account_url, credential=self.account_key)
            else:
                # For local development/testing without credentials
                self.blob_service_client = None
                print("Azure Storage not properly configured. Please set AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_ACCOUNT_NAME and AZURE_STORAGE_ACCOUNT_KEY in environment variables.")
                
        except Exception as e:
            print(f"Azure Storage initialization error: {e}")
            self.blob_service_client = None

    async def upload_image(self, file: UploadFile, folder: str = "questions") -> str:
        """
        Upload image to Azure Blob Storage
        
        Args:
            file: The image file to upload
            folder: The container name in Azure Blob Storage (e.g., "questions", "options")
            
        Returns:
            URL of the uploaded image
        """
        if not self.blob_service_client:
            raise ValueError("Azure Storage not initialized")
        
        # Create a unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Use the folder as container name and create subfolder structure if needed
        container_name = folder
        if "/" in folder:
            # If folder contains path separator, use the first part as container and rest as path
            parts = folder.split("/", 1)
            container_name = parts[0]
            blob_name = f"{parts[1]}/{unique_filename}"
        else:
            blob_name = unique_filename
        
        # Read the file content
        content = await file.read()
        
        try:
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name, 
                blob=blob_name
            )
            
            # Upload the file
            blob_client.upload_blob(content, overwrite=True)
            
            # Return public URL
            return blob_client.url
            
        except Exception as e:
            raise e
    
    def delete_image(self, image_url: str) -> bool:
        """
        Delete an image from Azure Blob Storage
        
        Args:
            image_url: The public URL of the image to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.blob_service_client or not image_url:
            return False
        
        try:
            # Extract container and blob name from URL
            # URL format: https://ACCOUNT_NAME.blob.core.windows.net/CONTAINER_NAME/BLOB_NAME
            url_parts = image_url.split('/')
            if len(url_parts) >= 5 and 'blob.core.windows.net' in image_url:
                container_name = url_parts[3]
                blob_name = '/'.join(url_parts[4:])
                
                # Get blob client and delete
                blob_client = self.blob_service_client.get_blob_client(
                    container=container_name, 
                    blob=blob_name
                )
                
                if blob_client.exists():
                    blob_client.delete_blob()
                    return True
                    
            return False
        except Exception as e:
            print(f"Error deleting image: {e}")
            return False

    def get_blob_url(self, container_name: str, blob_name: str) -> str:
        """
        Get the public URL for a blob
        
        Args:
            container_name: Name of the container
            blob_name: Name of the blob
            
        Returns:
            Public URL of the blob
        """
        if not self.blob_service_client:
            raise ValueError("Azure Storage not initialized")
            
        blob_client = self.blob_service_client.get_blob_client(
            container=container_name, 
            blob=blob_name
        )
        return blob_client.url