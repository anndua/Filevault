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
                     user_id:int,
                     data:BinaryIO)->Chunk:
        
        
        
        upload_session=self.upload_session_repository.get_by_upload_id(upload_id)
        if upload_session is None or upload_session.owner_id != user_id:
            raise UploadSessionNotFound()
        if upload_session.status != "INITIATED":
            raise UploadSessionNotFound()
        if chunk_number < 1 or chunk_number > upload_session.total_chunks:
            raise ValueError("chunk number is outside the upload session range")
        exisiting_chunk=self.chunk_repository.get_chunk(upload_session.id,chunk_number)
        if exisiting_chunk:
            return exisiting_chunk
        chunk_key=f"uploads/{upload_id}/chunk-{chunk_number}"
        data.seek(0, 2)
        chunk_size = data.tell()
        data.seek(0)
        self.storage.put(key=chunk_key,data=data)
        chunk=Chunk(
            UploadSession_id=upload_session.id,
            chunk_number=chunk_number,
            object_key=chunk_key,
            size=chunk_size
        )
        saved_chunk = self.chunk_repository.create(chunk)
        upload_session.uploaded_chunks+=1
        self.upload_session_repository.update(upload_session)
        return saved_chunk
    
        

        