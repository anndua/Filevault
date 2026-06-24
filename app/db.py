from sqlmodel import SQLModel,Session,create_engine
from config import DATABASE_URL

assert DATABASE_URL
engine =create_engine(DATABASE_URL)
def get_session():
    with Session(engine) as session:
        yield session


