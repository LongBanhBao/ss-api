from sqlmodel import SQLModel, Session, create_engine
from typing import Annotated
from fastapi import Depends
from app.config import get_settings

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

DATABASE_URL = get_settings().DATABASE_URL


engine = create_engine(url=DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


SessionDep = Annotated[Session, Depends(get_session)]
