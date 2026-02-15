import os
import uuid
import aiofiles
from fastapi import UploadFile
from config import get_settings

settings = get_settings()


class StorageService:
    def __init__(self):
        # Use local storage directory
        self.storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
        self.base_url = settings.backend_url

        # Create uploads directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_user_dir(self, user_id: str) -> str:
        """Get or create user-specific upload directory."""
        user_dir = os.path.join(self.storage_dir, user_id)
        os.makedirs(user_dir, exist_ok=True)
        return user_dir

    async def upload_file(self, file: UploadFile, user_id: str) -> dict:
        """Upload a file to local storage and return metadata."""
        # Generate unique filename
        file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
        unique_id = str(uuid.uuid4())
        unique_filename = f"{unique_id}.{file_extension}"

        # Get user directory
        user_dir = self._get_user_dir(user_id)
        file_path = os.path.join(user_dir, unique_filename)

        # Read and save file
        content = await file.read()
        file_size = len(content)

        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)

        # Generate URL path (relative to uploads)
        relative_path = f"{user_id}/{unique_filename}"
        public_url = f"{self.base_url}/uploads/{relative_path}"

        return {
            "filename": relative_path,
            "original_filename": file.filename,
            "storage_url": public_url,
            "file_size": file_size,
            "mime_type": file.content_type,
        }

    def delete_file(self, filename: str) -> bool:
        """Delete a file from local storage."""
        try:
            file_path = os.path.join(self.storage_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception:
            return False

    def get_file_path(self, filename: str) -> str:
        """Get the full file path for a file."""
        return os.path.join(self.storage_dir, filename)


# Singleton instance
storage_service = StorageService()
