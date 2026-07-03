from models import UploadSession

from repositories.upload_session_repository import UploadSessionRepository
from utils.object_key import ObjectkeyGenerator

class UploadSessionService:
    def __init__(self,upload_session_repository:UploadSessionRepository):
        self.upload_session_repository= upload_session_repository
    def initiate_upload(
            self,user_id:int,
            filename:str,
            total_chunks:int):
        key=ObjectkeyGenerator.generate(user_id=user_id,
                                        filename=filename)
        
    