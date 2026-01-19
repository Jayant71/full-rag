from abc import ABC, abstractmethod
import os
import shutil
from app.core.config import settings
from typing import Optional


class BaseStorage(ABC):
    @abstractmethod
    def upload(self, file_path: str, filename: str, user_id: Optional[str] = None, space_id: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def get_path(self, storage_key: str) -> str:
        pass

    @abstractmethod
    def delete(self, storage_key: str) -> bool:
        pass


class LocalStorage(BaseStorage):
    def __init__(self):
        self.upload_dir = "app_data/uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    def upload(self, file_path: str, filename: str, user_id: Optional[str] = None, space_id: Optional[str] = None) -> str:
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


def get_storage_engine() -> BaseStorage:
    storage_type = settings.STORAGE_TYPE.lower()

    if storage_type == "local":
        return LocalStorage()
    else:
        raise ValueError(
            f"Unsupported STORAGE_TYPE: {settings.STORAGE_TYPE}. Use 'local', 's3', or 'supabase'.")
