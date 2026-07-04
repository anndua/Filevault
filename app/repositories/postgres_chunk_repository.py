from sqlmodel import Session,select

from models import chunk

from repositories.chunk_repositiry import ChunkRepository


class PostgressChunkRepository(ChunkRepository):
    def __init__(self,session:Session):
        self.session=session

    def create(self, chunk: chunk):
        self.session.add(chunk)
        self.session.commit()
        self.session.refresh(chunk)
        return chunk
    
    def get_chunk(self, upload_session_id: int, chunk_number: int):
        statement=select(chunk).where(chunk.UploadSession_id==upload_session_id,
                                      chunk.chunck_number==chunk_number)
        
        return self.session.exec(statement).first()
    def list_chunk(self,upload_session_id:int):
        statement=select(chunk).where(
            chunk.UploadSession_id==upload_session_id)
        return self.session.exec(statement)
    def delete(self,chunk:chunk):
        self.session.delete(chunk)
        self.session.commit()
        
        
