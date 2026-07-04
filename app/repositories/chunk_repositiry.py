from abc import ABC,abstractmethod
from models import chunk

class ChunkRepository(ABC):
    @abstractmethod

    def create(self,chunk:chunk):
        pass
    @abstractmethod
    def get_chunk(self,upload_session_id:int,
                  chunk_number:int):
        pass
    @abstractmethod
    def list_chunk(
        self,upload_session_id:int):
        pass
    @abstractmethod
    def delete(self,chunk:chunk):
        pass

    

    