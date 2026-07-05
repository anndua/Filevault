from uuid import UUID

from sqlmodel import Session,select

from models import UploadSession
from repositories.upload_session_repository import UploadSessionRepository

class PostgresUploadSessionRepository(UploadSessionRepository):
    def __init__(self,session:Session):
        self.session=session

    def create(self,upload_session:UploadSession):
        self.session.add(upload_session)
        self.session.commit()
        self.session.refresh(upload_session)

        return upload_session
    def get_by_upload_id(self,upload_id:UUID):
        statement=select(UploadSession).where(UploadSession.upload_id==upload_id)
        return self.session.exec(statement).first()
    def update(self,upload_session:UploadSession):
        self.session.add(upload_session)
        self.session.commit()
        self.session.refresh(upload_session)
        return upload_session
    def delete(self,upload_session:UploadSession):
        self.session.delete(upload_session)
        self.session.commit()
           
    
