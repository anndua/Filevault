from typing import BinaryIO
from uuid import UUID

from models import Chunk
from repositories.chunk_repositiry import ChunkRepository
from repositories.upload_session_repository import UploadSessionRepository
from storage.exceptions import UploadSessionNotFound
from storage.base import storageBackend


#                  ChunkService
#                       │
#       ┌───────────────┼────────────────┐
#       ▼               ▼                ▼
# UploadSessionRepo   ChunkRepo      Storage

class ChunkService:
    def __init__(self,storage:storageBackend,upload_session_repository:UploadSessionRepository,
                 chunk_repository:ChunkRepository):
        self.storage=storage
        self.upload_session_repository=upload_session_repository
        self.chunk_repository=chunk_repository
    def upload_chunk(self,upload_id:UUID,
                     chunk_number:int,
                     data:BinaryIO):
        upload_session=self.upload_session_repository.get_by_upload_id(upload_id)
        if upload_session is None:
            raise UploadSessionNotFound()
        exisiting_chunk=self.chunk_repository.get_chunk(upload_session.id,chunk_number)
        if exisiting_chunk:
            return exisiting_chunk
        chunk_key=f"uploads/{upload_id}/chunk-{chunk_number}"
        self.storage.put(key=chunk_key,data=data)
        chunk=Chunk(
            UploadSession_id=upload_session.id,
            chunk_number=chunk_number,
            object_key=chunk_key,
            size=0
        )
        saved_chunk = self.chunk_repository.create(chunk)
        upload_session.uploaded_chunks+=1
        self.upload_session_repository.update(upload_session)
        return saved_chunk
    
        

        