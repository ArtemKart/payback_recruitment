from typing import Generator

from sqlalchemy import event, Engine
from sqlmodel import create_engine, SQLModel, Session

from app.infrastructure.config import get_settings

settings = get_settings()

_engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    echo=settings.DATABASE_ECHO,
)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, _connection_record) -> None:
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def get_engine() -> Engine:
    return _engine


def create_db_and_tables() -> None:
    engine = get_engine()
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    engine = get_engine()
    with Session(engine) as session:
        yield session
