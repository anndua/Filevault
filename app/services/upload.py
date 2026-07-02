# HTTP Request
#       │
#       ▼
# Router
#       │
#       ▼
# UploadService
#       │
#       ▼
# StorageBackend
#       │
#       ▼
# LocalStorage

from typing import BinaryIO
from storage.base import storageBackend
from utils.object_key import ObjectkeyGenerator
from repositories.file_repository import FileRepsitory
from storage.exceptions import FileNotFound
from models import File
class UploadServices:
    def __init__(self,storage:storageBackend,file_repository:FileRepsitory):
        self.storage = storage
        self.file_repository=file_repository
    def upload(self,user_id:int,filename:str,content_type:str,data:BinaryIO):
        key=ObjectkeyGenerator.generate(user_id=user_id,filename=filename)
        try:
            self.storage.put(key=key,
                             data=data)
            file=File(
                filename=filename,
                object_key=key,
                owner_id=user_id,
                content_type=content_type,
                size=0,
                status="READY"
            )
            return self.file_repository.create(file)
        except Exception:
            if self.storage.exists(key):

                self.storage.delete(key)
            raise
        

        
    
    def download(self,key:str)->BinaryIO:
        return self.storage.get(key=key)
    def delete_file(self, file_id: int):

        file = self.file_repository.get(file_id)

        if file is None:
            raise FileNotFound()

        self.storage.delete(file.object_key)
        self.file_repository.delete(file)
        
    def exist(self,key:str)->bool:
        return self.storage.exists(key=key)
    def list_files(self,owner_id:int):
        return self.file_repository.list_by_owner(owner_id)
    def get_file(self,file_id:int):
        file =self.file_repository.get(file_id)
        if file is None:
            raise FileNotFound()
        return file

    
    
    





        