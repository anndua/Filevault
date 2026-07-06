from uuid import UUID
from repositories.upload_session_repository import UploadSessionRepository
from repositories.postgres_chunk_repository import ChunkRepository
from storage.exceptions import UploadSessionNotFound,UploadIncomplete

class CompleteUploadService:
    def __init__(
            self,upload_session_repository:UploadSessionRepository,
            chunk_repository:ChunkRepository
    ):
        self.upload_session_repository=upload_session_repository
        self.chunk_repository=chunk_repository
    def complete_upload(self,upload_id:UUID):
        upload_session =self.upload_session_repository.get_by_upload_id(upload_id)

        if upload_session is None:
            raise UploadSessionNotFound
        chunks=self.chunk_repository.list_chunks(upload_session.id)
        if len(chunks)!=upload_session.total_chunks:
            raise UploadIncomplete
            
