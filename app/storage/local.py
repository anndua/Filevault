from pathlib import Path
from typing import BinaryIO
import shutil

from storage.base import storageBackend
from storage.exceptions import (
    ObjectNotFound,
    StoragePermissionDenied,
    StorageError,
)


class LocalStrorage(storageBackend):
    def __init__(self,root:Path):
        self.root=root

    def put(self,key:str,data:BinaryIO)->None:
        Path=self.root/key
        try:


            Path.parent.mkdir(
            parents=True,
            exist_ok=True)
        
            with open(Path,"wb") as file:

                shutil.copyfileobj(data,file)
            #copyfilobj does readsmall chunk wrote small chunk read next chunk until EOF
        except PermissionError as e:
            raise StoragePermissionDenied(
                f"permission denied while storing '{key}'"
            )from e
        except OSError as e:
            raise StorageError(
                f"faled to store '{key}'"
            )from e
           
    
    def get(self,key:str)->BinaryIO:
        path=self.root/key
        try:
            return open(path,"rb")
        except FileNotFoundError as e:
            raise ObjectNotFound(f"öbject '{key}' not found")from e
        except OSError as e:
            raise StorageError(
                f"failed to read object '{key}'"
            )from e
        
        

        
    


        
    def delete(self,key:str)->None:
        path=self.root/key
        try:

        
            path.unlink()
        except FileNotFoundError as e:
            raise ObjectNotFound(
                f"object '{key}' not found"
            )from e
        except PermissionError as e:
            raise StoragePermissionDenied(
                f"permission denied while deleting '{key}'"
            )from e
        
        

        
    def exists(self,key:str)->bool:
        path=self.root/key
        return path.exists()


# Goal

# When someone writes:

# storage.put(
#     key="users/42/avatar.png",
#     data=stream
# )

# we want this to happen:

# key
#  │
#  ▼
# storage_data/objects/users/42/avatar.png

# ↓

# Create directories if needed

# ↓

# Write stream to disk

# ↓

# Done

