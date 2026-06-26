#what capabilities must every storage backen have?
# Storage Backend Requirements

# ✓ Store an object
# ✓ Retrieve an object
# ✓ Delete an object
# ✓ Check existence

#this is basically a specification file
from abc import ABC,abstractmethod
from typing import BinaryIO
#ABC mean this class is incomplete->abstract base class let us create class whoe purpose is to define contract not an implementation

class storageBackend(ABC):
    @abstractmethod
    def put(self,key:str,data:BinaryIO,)->None:
        pass
        #we using Binaryio is a type hint tells read bytes from something
    @abstractmethod
    def get(self,keY:str)->BinaryIO:
        pass
    #binaryio nothing is loaded at once read small chunks sen read next chuck send 
    @abstractmethod
    def delete(self,key:str)->None:
        pass
    @abstractmethod
    def exists(
    self,
    key: str,
) -> bool:
       pass

