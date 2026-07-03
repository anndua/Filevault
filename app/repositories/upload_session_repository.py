from abc import ABC, abstractmethod
from uuid import UUID
from models import UploadSession


class UploadSessionRepository(ABC):

    @abstractmethod
    def create(self,session:UploadSession):
        pass
    @abstractmethod
    def get_by_upload_id(
        self,
        upload_id:UUID):
        pass
    @abstractmethod
    def update(self,session:UploadSession):
        pass
    @abstractmethod
    def delete(self,session:UploadSession):
        pass
    