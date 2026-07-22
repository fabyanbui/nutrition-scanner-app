import os
from abc import ABC, abstractmethod
import uuid
import aiofiles
from .config import settings

class StorageProvider(ABC):
    @abstractmethod
    async def upload(self, file_bytes: bytes, content_type: str) -> str:
        pass

    @abstractmethod
    async def download(self, file_id: str) -> bytes:
        pass

    @abstractmethod
    async def delete(self, file_id: str) -> bool:
        pass

class LocalStorageProvider(StorageProvider):
    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    async def upload(self, file_bytes: bytes, content_type: str) -> str:
        ext = "jpg"
        if "png" in content_type:
            ext = "png"
        elif "webp" in content_type:
            ext = "webp"
            
        file_id = f"{uuid.uuid4()}.{ext}"
        path = os.path.join(self.storage_dir, file_id)
        
        async with aiofiles.open(path, 'wb') as f:
            await f.write(file_bytes)
            
        return file_id

    async def download(self, file_id: str) -> bytes:
        path = os.path.join(self.storage_dir, file_id)
        if not os.path.exists(path):
            raise FileNotFoundError(f"File {file_id} not found")
            
        async with aiofiles.open(path, 'rb') as f:
            return await f.read()

    async def delete(self, file_id: str) -> bool:
        path = os.path.join(self.storage_dir, file_id)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

# Factory
def get_storage() -> StorageProvider:
    if settings.STORAGE_PROVIDER == "local":
        return LocalStorageProvider(settings.STORAGE_LOCAL_DIR)
    # Add supabase or others later
    return LocalStorageProvider(settings.STORAGE_LOCAL_DIR)
