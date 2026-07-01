from abc import ABC, abstractmethod

from models import File

class FileRepsitory(ABC):
    @abstractmethod
    def create(self,file:File):
        pass

    @abstractmethod
    def get(self,file_id:int):
        pass
    @abstractmethod
    def delete(self,file_id:int):
        pass
    @abstractmethod
    def list_by_owner(self,owner_id:int):
        pass
    