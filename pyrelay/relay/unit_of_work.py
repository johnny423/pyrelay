import abc
from typing import Optional, Self

from sqlalchemy.ext.asyncio import AsyncSession

from pyrelay.relay.relay_service import EventsRepository, Subscriptions
from pyrelay.relay.repos.sqlalchemy_event_repo import SqlAlchemyEventRepository


class UnitOfWork:
    """
    Context manager which setup the resources atomic execution
    over the shared state
    """

    events: EventsRepository
    subscriptions: Subscriptions

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exn_type, exn_value, traceback) -> None:
        if exn_type is None:
            await self.commit()
        else:
            await self.rollback()

    @abc.abstractmethod
    async def commit(self) -> None:
        """
        Committing all the work being done in this context
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self) -> None:
        """
        Undoing all the work being done in this context
        """
        raise NotImplementedError


class SqlAlchemyUOW(UnitOfWork):
    def __init__(self, session_factory, subscriptions):
        self.session_factory = session_factory
        self.subscriptions = subscriptions
        self.session: Optional[AsyncSession] = None

    async def __aenter__(self):
        self.session = self.session_factory()
        await self.session.begin()
        self.events = SqlAlchemyEventRepository(self.session)
        return await super().__aenter__()

    async def __aexit__(self, exn_type, exn_value, traceback):
        await super().__aexit__(exn_type, exn_value, traceback)
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()


class InMemoryUOW(UnitOfWork):
    def __init__(self, subscriptions, repo):
        self.subscriptions = subscriptions
        self.events = repo

    async def commit(self) -> None:
        return

    async def rollback(self) -> None:
        return
