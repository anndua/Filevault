from typing import Literal

from sqlmodel import Session, func, select

from models import File

from repositories.file_repository import FileRepsitory

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
    def list_by_owner(
        self,
        owner_id: int,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
        sort_by: Literal["filename", "size", "created_at"] = "created_at",
        sort_order: Literal["asc", "desc"] = "desc",
    ):
        statement=select(File).where(File.owner_id==owner_id)
        if search:
            statement = statement.where(File.filename.ilike(f"%{search}%"))
        sort_column = {
            "filename": File.filename,
            "size": File.size,
            "created_at": File.created_at,
        }[sort_by]
        statement = statement.order_by(
            sort_column.asc() if sort_order == "asc" else sort_column.desc(),
            File.id.asc() if sort_order == "asc" else File.id.desc(),
        )
        return list(self.session.exec(statement.offset(offset).limit(limit)))

    def count_by_owner(self, owner_id: int, search: str | None = None) -> int:
        statement = select(func.count()).select_from(File).where(File.owner_id == owner_id)
        if search:
            statement = statement.where(File.filename.ilike(f"%{search}%"))
        return self.session.exec(statement).one()
