from sqlmodel import Session,select

from models import Chunk

from repositories.chunk_repositiry import ChunkRepository


class PostgressChunkRepository(ChunkRepository):
    def __init__(self,session:Session):
        self.session=session

    def create(self, chunk: Chunk):
        self.session.add(chunk)
        self.session.commit()
        self.session.refresh(chunk)
        return chunk
    
    def get_chunk(self, upload_session_id: int, chunk_number: int):
        statement=select(Chunk).where(Chunk.UploadSession_id==upload_session_id,
                                      Chunk.chunk_number==chunk_number)
        return self.session.exec(statement).first()
    def list_chunk(self,upload_session_id:int):
        
        statement=select(Chunk).where(
            Chunk.UploadSession_id==upload_session_id)
        return self.session.exec(statement).all()
    def delete(self,chunk:Chunk):
        self.session.delete(chunk)
        self.session.commit()
        
        
