from sqlmodel import Session,select

from models import File

from file_repository import FileRepsitory

class PostgresFileRepository(FileRepsitory):
    def __init__(self,session:Session):
        self.session=session

    def create(self,file:File):
        self.session.add(file)
        self.session.commit()
        self.session.refresh(file)
        return file
    def get(self,file_id:int):
        statement=select(File).where(File.id==file_id)
        return self.session.exec(statement).first()         
    
    def delete(self,file:File):
        self.session.delete(file)
        self.session.commit()
    def list_by_owner(self, owner_id: int):
        statement=select(File).where(File.owner_id==owner_id)
        return list(self.session.exec(statement))
