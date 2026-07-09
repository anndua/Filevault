from uuid import UUID
from repositories.upload_session_repository import UploadSessionRepository
from repositories.chunk_repositiry import ChunkRepository
from storage.exceptions import UploadSessionNotFound,UploadIncomplete
from storage.base import storageBackend
from repositories.file_repository import FileRepsitory
import shutil
from tempfile import TemporaryFile
from models import File

class CompleteUploadService:
    def __init__(self,
                storage:storageBackend,
                upload_session_repository:UploadSessionRepository,
                chunk_repository:ChunkRepository,
                file_repository:FileRepsitory):
        self.storage=storage
        self.upload_session_repository=upload_session_repository
        self.chunk_repository=chunk_repository
        self.file_repository=file_repository

        
        
    def complete_upload(self,upload_id:UUID):
        upload_session =self.upload_session_repository.get_by_upload_id(upload_id)

        if upload_session is None:
            raise UploadSessionNotFound()
        chunks=self.chunk_repository.list_chunk(upload_session.id)
        if len(chunks)!=upload_session.total_chunks:
            raise UploadIncomplete()
        chunks.sort(key=lambda chunk:chunk.chunk_number)
        with TemporaryFile() as temp_file:
            for chunk in chunks:
                with self.storage.get(chunk.object_key) as chunk_stream:
                    shutil.copyfileobj(chunk_stream,temp_file)
                    
                
            temp_file.seek(0)#move back pointer to start after loop    
            self.storage.put(key=upload_session.object_key,
                            data=temp_file)
        size = sum(chunk.size for chunk in chunks)    
        file = File(
            filename=upload_session.filename,
            object_key=upload_session.object_key,
            size=size,
            content_type="application/octet-stream",
            owner_id=upload_session.owner_id,)
        file=self.file_repository.create(file)
        for chunk in chunks:
            self.storage.delete(chunk.object_key)
        for chunk in chunks:
            self.chunk_repository.delete(chunk)   
        upload_session.status = "COMPLETED"
        self.upload_session_repository.update(upload_session)  

        return file
        
    
              



            

