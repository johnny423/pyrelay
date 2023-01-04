from typing import Optional

from sqlalchemy.orm import sessionmaker

from pynostr.relay.config import settings
from pynostr.relay.db.session import start_engine, start_session, upgrade
from pynostr.relay.db.tables import init_mapper


def set_up_session_maker(
    sync_uri: Optional[str] = None, async_uri: Optional[str] = None
) -> sessionmaker:
    sync_uri = sync_uri or settings.SQLALCHEMY_DATABASE_URI

    upgrade(sync_uri)
    init_mapper()

    async_uri = async_uri or settings.ASYNC_SQLALCHEMY_DATABASE_URI
    engine = start_engine(async_uri)
    return start_session(engine)


