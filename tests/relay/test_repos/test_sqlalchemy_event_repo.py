import os

import pytest
import pytest_asyncio
from sqlalchemy.orm import clear_mappers

from pyrelay.relay.bootstrap import set_up_session_maker
from pyrelay.relay.db.tables import mapper_registry
from pyrelay.relay.unit_of_work import SqlAlchemyUOW
from tests.relay.test_repos.base_test_repo import (
    EventRepoTestBase,
    EventRepoNoFilters,
    EventRepoIdsFilters,
    EventRepoAuthorsFilters,
    EventRepoKindsFilters,
    EventRepoTimesFilters,
    EventRepoTagsFilters,
    EventRepoAllFilters,
    EventRepoEventSave,
)


class SqlalchemyTestMixin(EventRepoTestBase):
    @pytest.fixture(scope="class")
    def session_maker(
            self,
    ):
        filename = "test.db"
        yield set_up_session_maker(
            f"sqlite:///{filename}", f"sqlite+aiosqlite:///{filename}"
        )
        os.remove(f"{filename}")
        clear_mappers()

    @pytest_asyncio.fixture()
    async def uow(self, session_maker):
        yield SqlAlchemyUOW(session_maker, None)

        await self.tables_cleanup(session_maker)

    async def tables_cleanup(self, session_maker):
        async with session_maker() as s:
            for table in reversed(mapper_registry.metadata.sorted_tables):
                await s.execute(table.delete())
            await s.commit()


class TestSqlAlchemyEventRepoNoFilters(SqlalchemyTestMixin, EventRepoNoFilters):
    ...


class TestSqlAlchemyEventRepoIdsFilters(SqlalchemyTestMixin, EventRepoIdsFilters):
    ...


class TestSqlAlchemyEventRepoAuthorsFilters(
    SqlalchemyTestMixin, EventRepoAuthorsFilters
):
    ...


class TestSqlAlchemyEventRepoKindsFilters(SqlalchemyTestMixin, EventRepoKindsFilters):
    ...


class TestSqlAlchemyEventRepoTimesFilters(SqlalchemyTestMixin, EventRepoTimesFilters):
    ...


class TestSqlAlchemyEventRepoTagsFilters(SqlalchemyTestMixin, EventRepoTagsFilters):
    ...


class TestSqlAlchemyEventRepoAllFilters(SqlalchemyTestMixin, EventRepoAllFilters):
    ...


class TestSqlAlchemyEventRepoEventSave(SqlalchemyTestMixin, EventRepoEventSave):
    ...
