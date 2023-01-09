from typing import Callable, Optional

from sqlalchemy.orm import sessionmaker

from pyrelay.relay.config import settings
from pyrelay.relay.db.session import start_engine, start_session, upgrade
from pyrelay.relay.db.tables import init_mapper
from pyrelay.relay.relay_service import Subscriptions
from pyrelay.relay.repos.in_memory_event_repo import InMemoryEventsRepository
from pyrelay.relay.unit_of_work import InMemoryUOW, SqlAlchemyUOW, UnitOfWork


def set_up_session_maker(
    sync_uri: Optional[str] = None, async_uri: Optional[str] = None
) -> sessionmaker:
    sync_uri = sync_uri or settings.SQLALCHEMY_DATABASE_URI

    upgrade(sync_uri)
    init_mapper()

    async_uri = async_uri or settings.ASYNC_SQLALCHEMY_DATABASE_URI
    engine = start_engine(async_uri)
    return start_session(engine)


def get_uow_factory(in_memory: bool = False) -> Callable[[], UnitOfWork]:
    subscriptions = Subscriptions()
    if in_memory:
        repo = InMemoryEventsRepository()
        return lambda: InMemoryUOW(subscriptions, repo)
    else:
        session_maker = set_up_session_maker()
        return lambda: SqlAlchemyUOW(session_maker, subscriptions)
