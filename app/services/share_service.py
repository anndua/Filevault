from datetime import UTC, datetime, timedelta
import hashlib
import secrets

from models import File, ShareLink
from repositories.file_repository import FileRepsitory
from repositories.share_repository import ShareRepository
from storage.base import storageBackend
from storage.exceptions import FileAccessDenied, FileNotFound, ShareNotFound


class ShareExpired(Exception):
    pass


class ShareLimitReached(Exception):
    pass


class ShareService:
    def __init__(
        self,
        storage: storageBackend,
        file_repository: FileRepsitory,
        share_repository: ShareRepository,
    ):
        self.storage = storage
        self.file_repository = file_repository
        self.share_repository = share_repository

    def create(
        self,
        file_id: int,
        owner_id: int,
        expires_in_hours: int,
        max_downloads: int | None,
    ) -> tuple[ShareLink, str]:
        file = self.file_repository.get(file_id)
        if file is None:
            raise FileNotFound()
        if file.owner_id != owner_id:
            raise FileAccessDenied()

        token = secrets.token_urlsafe(32)
        share = ShareLink(
            token_hash=self._hash_token(token),
            file_id=file_id,
            owner_id=owner_id,
            expires_at=datetime.now(UTC) + timedelta(hours=expires_in_hours),
            max_downloads=max_downloads,
        )
        return self.share_repository.create(share), token

    def list_for_file(self, file_id: int, owner_id: int) -> list[ShareLink]:
        file = self.file_repository.get(file_id)
        if file is None:
            raise FileNotFound()
        if file.owner_id != owner_id:
            raise FileAccessDenied()
        return self.share_repository.list_for_file(file_id, owner_id)

    def revoke(self, share_id: int, file_id: int, owner_id: int) -> ShareLink:
        share = self.share_repository.get_for_owner(share_id, file_id, owner_id)
        if share is None:
            raise ShareNotFound()
        share.revoked = True
        return self.share_repository.save(share)

    def get_download_url(self, token: str) -> str:
        share = self.share_repository.get_by_token_hash(self._hash_token(token), lock=True)
        if share is None or share.revoked:
            raise ShareNotFound()
        if self._as_utc(share.expires_at) <= datetime.now(UTC):
            raise ShareExpired()
        if share.max_downloads is not None and share.download_count >= share.max_downloads:
            raise ShareLimitReached()

        file = self.file_repository.get(share.file_id)
        if file is None:
            raise ShareNotFound()
        url = self.storage.generate_download_url(
            key=file.object_key,
            expires_in=timedelta(minutes=5),
            filename=file.filename,
        )
        share.download_count += 1
        self.share_repository.save(share)
        return url

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
