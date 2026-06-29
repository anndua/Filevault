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


class UploadServices:
    def __init__(self,storage:storageBackend):
        self.storage = storage
    def upload(self,user_id:int,filename:str,data:BinaryIO):
        key=ObjectkeyGenerator.generate(user_id=user_id,filename=filename)

        self.storage.put(key=key,data=data)
        return key #->withut return router wudnt know wat we create cox router is related to fastapi fastapi always requires return
    def download(self,key:str)->BinaryIO:
        return self.storage.get(key=key)
    def delete(self,key:str)->None:
        self.storage.delete(key=key)
    def exist(self,key:str)->bool:
        return self.storage.exists(key=key)
    





        