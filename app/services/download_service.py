from datetime import timedelta

from repositories.file_repository import FileRepsitory
from storage.base import storageBackend

from uuid import UUID
from models import User
from storage.exceptions import FileAccessDenied, FileNotFound

class DownloadService:
    def __init__(
            self,
            storage:storageBackend,
            file_repository:FileRepsitory
    ):
        self.storage=storage
        self.file_repository=file_repository
    def get_download_url(self, file_id: int, user: User) -> str:
        file = self.file_repository.get(file_id)
        if file is None:
            raise FileNotFound()
        if file.owner_id != user.id:
            raise FileAccessDenied()
        return self.storage.generate_download_url(
            key=file.object_key,
            expires_in=timedelta(minutes=5),
            filename=file.filename,
        )
        
