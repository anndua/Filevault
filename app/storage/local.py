from pathlib import Path
from typing import BinaryIO
import shutil

from storage.base import storageBackend


class LocalStrorage(storageBackend):
    def __init__(self,root:Path):
        self.root=root

    def put(self,key:str,data:BinaryIO)->None:
        Path=self.root/key
        Path.parent.mkdir(
            parents=True,
            exist_ok=True
        )
        with open(Path,"wb") as file:
            shutil.copyfileobj(data,file)
            #copyfilobj does readsmall chunk wrote small chunk read next chunk until EOF
        pass
    def get(self,key:str)->BinaryIO:
        path=self.root/key
        return open(pathath,"rb")
    


        
    def delete(self,key:str)->None:
        path=self.root/key
        path.unlink()
        

        
    def exist(self,key:str)->bool:
        pass


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

