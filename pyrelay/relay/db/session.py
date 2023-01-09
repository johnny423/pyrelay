import os

from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

CURRENT_FILE = os.path.dirname(os.path.realpath(__file__))


def upgrade(uri: str) -> None:
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", CURRENT_FILE + "/../../alembic")
    alembic_cfg.set_main_option("sqlalchemy.url", uri)
    command.upgrade(alembic_cfg, "head")


def start_engine(uri: str) -> AsyncEngine:
    return create_async_engine(uri, pool_pre_ping=True)


def start_session(engine: AsyncEngine) -> sessionmaker:
    return sessionmaker(
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncSession,
    )
