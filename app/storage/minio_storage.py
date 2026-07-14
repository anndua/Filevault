from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from storage.base import storageBackend
from storage.exceptions import ObjectNotFound,StoragePermissionDenied,StorageError

class MinioStorage(storageBackend):
    def __init__(self,endpoint:str,access_key:str,secret_key:str,bucket:str,secure:bool=False):
        self.client=Minio(endpoint=endpoint,access_key=access_key,
                          secret_key=secret_key,
                          secure=secure)
        
        self.bucket=bucket
        print(">>> MinioStorage initialized")
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
    def put(self,key:str,data:BinaryIO)->None:
        current=data.tell()#tell where current pointer is
        
        data.seek(0,2)#move to end
        size=data.tell()#tell now where pointer is basically that will be equal size of the file
        data.seek(current)#restore pointer to start
        try:
            self.client.put_object(bucket_name=self.bucket,
                                   object_name=key,
                                   data=data,
                                   length=size)
        except PermissionError as e:
            raise StoragePermissionDenied(
                f"permission denied while storing '{key}'"
            )from e
        except S3Error as e:
            raise StorageError(
                f"Failed to store '{key}'"
            )from e    
    def exists(self, key: str)->bool:
        try:
            self.client.stat_object(bucket_name=self.bucket,
                                    object_name=key)
            return True
        except Exception:
            return False
    def get(self,key:str):
        try:
            return self.client.get_object(bucket_name=self.bucket,
                                          object_name=key)
        
           
           
        except Exception  as e:
            raise StorageError(f"Failed to retieve '{key}'")from e
    def delete(self,key:str):
        try:
            self.client.remove_object(bucket_name=self.bucket,
                                      object_name=key)
        except Exception as e:
            raise StorageError(
                f"Falied to delete '{key}'"
            )from e
                
         
        
       
