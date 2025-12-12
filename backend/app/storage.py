"""
Storage Engine with support for Local, S3, and Supabase Storage.
"""
from abc import ABC, abstractmethod
import os
import shutil
import tempfile
import boto3
import httpx
from botocore.exceptions import NoCredentialsError
from app.config import settings


class BaseStorage(ABC):
    @abstractmethod
    def upload(self, file_path: str, filename: str, user_id: str = None, space_id: str = None) -> str:
        """Uploads a file and returns a storage key/path."""
        pass

    @abstractmethod
    def get_path(self, storage_key: str) -> str:
        """Returns a local path or URL for the file."""
        pass
    
    @abstractmethod
    def delete(self, storage_key: str) -> bool:
        """Deletes a file from storage."""
        pass


class LocalStorage(BaseStorage):
    def __init__(self):
        self.upload_dir = "app_data/uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    def upload(self, file_path: str, filename: str, user_id: str = None, space_id: str = None) -> str:
        # Create user/space subdirectory if provided
        if user_id and space_id:
            target_dir = os.path.join(self.upload_dir, user_id, space_id)
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, filename)
            storage_key = f"{user_id}/{space_id}/{filename}"
        else:
            target_path = os.path.join(self.upload_dir, filename)
            storage_key = filename
        
        shutil.copy(file_path, target_path)
        return storage_key

    def get_path(self, storage_key: str) -> str:
        return os.path.join(self.upload_dir, storage_key)
    
    def delete(self, storage_key: str) -> bool:
        file_path = os.path.join(self.upload_dir, storage_key)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False


class S3Storage(BaseStorage):
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION
        )
        self.bucket = settings.S3_BUCKET_NAME

    def upload(self, file_path: str, filename: str, user_id: str = None, space_id: str = None) -> str:
        # Create a key with user/space prefix if provided
        if user_id and space_id:
            key = f"{user_id}/{space_id}/{filename}"
        else:
            key = filename
        
        try:
            self.s3.upload_file(file_path, self.bucket, key)
            return key
        except NoCredentialsError:
            raise ValueError("S3 Credentials not available")

    def get_path(self, storage_key: str) -> str:
        # Download to temp file for processing
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(storage_key)[1])
        self.s3.download_file(self.bucket, storage_key, tmp.name)
        return tmp.name
    
    def delete(self, storage_key: str) -> bool:
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=storage_key)
            return True
        except Exception:
            return False


class SupabaseStorage(BaseStorage):
    """Storage using Supabase Storage (uses the 'documents' bucket)."""
    
    def __init__(self):
        self.bucket = "documents"
        self.base_url = settings.SUPABASE_URL
        self.service_key = settings.SUPABASE_SERVICE_KEY
        
        if not self.base_url or not self.service_key:
            raise ValueError("Supabase URL and Service Key are required for Supabase storage")

    def _get_headers(self) -> dict:
        return {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
        }

    def upload(self, file_path: str, filename: str, user_id: str = None, space_id: str = None) -> str:
        # Storage path: user_id/space_id/filename
        if user_id and space_id:
            storage_path = f"{user_id}/{space_id}/{filename}"
        else:
            storage_path = filename
        
        # Read file content
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        # Determine content type
        import mimetypes
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        
        # Upload to Supabase Storage
        url = f"{self.base_url}/storage/v1/object/{self.bucket}/{storage_path}"
        
        # Use synchronous request for simplicity
        import requests
        response = requests.post(
            url,
            headers={
                **self._get_headers(),
                "Content-Type": content_type,
            },
            data=file_content
        )
        
        if response.status_code not in [200, 201]:
            # Try update if file exists
            response = requests.put(
                url,
                headers={
                    **self._get_headers(),
                    "Content-Type": content_type,
                },
                data=file_content
            )
        
        if response.status_code not in [200, 201]:
            raise ValueError(f"Failed to upload to Supabase Storage: {response.text}")
        
        return storage_path

    def get_path(self, storage_key: str) -> str:
        # Download to temp file for processing
        url = f"{self.base_url}/storage/v1/object/{self.bucket}/{storage_key}"
        
        import requests
        response = requests.get(url, headers=self._get_headers())
        
        if response.status_code != 200:
            raise ValueError(f"Failed to download from Supabase Storage: {response.text}")
        
        # Save to temp file
        suffix = os.path.splitext(storage_key)[1]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(response.content)
        tmp.close()
        
        return tmp.name
    
    def delete(self, storage_key: str) -> bool:
        url = f"{self.base_url}/storage/v1/object/{self.bucket}/{storage_key}"
        
        import requests
        response = requests.delete(url, headers=self._get_headers())
        
        return response.status_code in [200, 204]


def get_storage_engine() -> BaseStorage:
    """Get the appropriate storage engine based on configuration."""
    storage_type = settings.STORAGE_TYPE.lower()
    
    if storage_type == "local":
        return LocalStorage()
    elif storage_type == "s3":
        return S3Storage()
    elif storage_type == "supabase":
        return SupabaseStorage()
    else:
        raise ValueError(f"Unsupported STORAGE_TYPE: {settings.STORAGE_TYPE}. Use 'local', 's3', or 'supabase'.")
