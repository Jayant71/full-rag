from abc import ABC, abstractmethod
import os
import boto3
from botocore.exceptions import NoCredentialsError
from app.config import settings

class BaseStorage(ABC):
    @abstractmethod
    def upload(self, file_path: str, filename: str) -> str:
        """Uploads a file and returns a storage key/path."""
        pass

    @abstractmethod
    def get_path(self, storage_key: str) -> str:
        """Returns a local path or URL for the file."""
        pass

class LocalStorage(BaseStorage):
    def __init__(self):
        self.upload_dir = "app_data/uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    def upload(self, file_path: str, filename: str) -> str:
        # In local storage, we just copy/move the file to the upload dir
        # For simplicity in this refactor, we assume the file is already in a temp location
        # and we move it to a permanent location.
        import shutil
        
        target_path = os.path.join(self.upload_dir, filename)
        shutil.copy(file_path, target_path)
        return target_path

    def get_path(self, storage_key: str) -> str:
        return storage_key

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

    def upload(self, file_path: str, filename: str) -> str:
        try:
            self.s3.upload_file(file_path, self.bucket, filename)
            return filename
        except NoCredentialsError:
            raise ValueError("S3 Credentials not available")

    def get_path(self, storage_key: str) -> str:
        # For S3, we might need to download it to a temp file for processing if the library requires a local path
        # Or return a presigned URL. LlamaParse can handle URLs if public, but for private S3/MinIO, 
        # downloading to temp is safer for processing.
        # However, for the purpose of "get_path" in this context, let's assume we download to temp.
        import tempfile
        
        # Create a temp file
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(storage_key)[1])
        self.s3.download_file(self.bucket, storage_key, tmp.name)
        return tmp.name

def get_storage_engine() -> BaseStorage:
    if settings.STORAGE_TYPE == "local":
        return LocalStorage()
    elif settings.STORAGE_TYPE == "s3":
        return S3Storage()
    else:
        raise ValueError(f"Unsupported STORAGE_TYPE: {settings.STORAGE_TYPE}")
