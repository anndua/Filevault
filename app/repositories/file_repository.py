from abc import ABC, abstractmethod
from typing import Literal

from models import File

class FileRepsitory(ABC):
    @abstractmethod
    def create(self,file:File):
        pass

    @abstractmethod
    def get(self,file_id:int):
        pass
    @abstractmethod
    def delete(self,file_id:File):
        pass
    @abstractmethod
    def list_by_owner(
        self,
        owner_id: int,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
        sort_by: Literal["filename", "size", "created_at"] = "created_at",
        sort_order: Literal["asc", "desc"] = "desc",
    ):
        pass

    @abstractmethod
    def count_by_owner(self, owner_id: int, search: str | None = None) -> int:
        pass
    