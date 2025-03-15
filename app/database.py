from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings

DATABASE_URL = get_settings().DATABASE_URL

url = f"sqlite:///test.db"

if not DATABASE_URL.startswith("postgresql"):
    engine = create_engine(url=url, echo=True)
else:
    engine = create_engine(url=DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


SessionDep = Annotated[Session, Depends(get_session)]
