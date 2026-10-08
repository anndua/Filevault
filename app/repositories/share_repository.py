from abc import ABC, abstractmethod

from models import ShareLink


class ShareRepository(ABC):
    @abstractmethod
    def create(self, share: ShareLink) -> ShareLink:
        raise NotImplementedError

    @abstractmethod
    def get_by_token_hash(self, token_hash: str, lock: bool = False) -> ShareLink | None:
        raise NotImplementedError

    @abstractmethod
    def get_for_owner(self, share_id: int, file_id: int, owner_id: int) -> ShareLink | None:
        raise NotImplementedError

    @abstractmethod
    def list_for_file(self, file_id: int, owner_id: int) -> list[ShareLink]:
        raise NotImplementedError

    @abstractmethod
    def save(self, share: ShareLink) -> ShareLink:
        raise NotImplementedError
