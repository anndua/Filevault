from sqlmodel import Session, select

from models import ShareLink
from repositories.share_repository import ShareRepository


class PostgresShareRepository(ShareRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, share: ShareLink) -> ShareLink:
        self.session.add(share)
        self.session.commit()
        self.session.refresh(share)
        return share

    def get_by_token_hash(self, token_hash: str, lock: bool = False) -> ShareLink | None:
        statement = select(ShareLink).where(ShareLink.token_hash == token_hash)
        if lock:
            statement = statement.with_for_update()
        return self.session.exec(statement).first()

    def get_for_owner(
        self, share_id: int, file_id: int, owner_id: int
    ) -> ShareLink | None:
        statement = select(ShareLink).where(
            ShareLink.id == share_id,
            ShareLink.file_id == file_id,
            ShareLink.owner_id == owner_id,
        )
        return self.session.exec(statement).first()

    def list_for_file(self, file_id: int, owner_id: int) -> list[ShareLink]:
        statement = (
            select(ShareLink)
            .where(ShareLink.file_id == file_id, ShareLink.owner_id == owner_id)
            .order_by(ShareLink.created_at.desc(), ShareLink.id.desc())
        )
        return list(self.session.exec(statement))

    def save(self, share: ShareLink) -> ShareLink:
        self.session.add(share)
        self.session.commit()
        self.session.refresh(share)
        return share
