import os

import pytest
import pytest_asyncio

from pyrelay.relay.bootstrap import set_up_session_maker
from pyrelay.relay.db.tables import mapper_registry
from pyrelay.relay.repos.sqlalchemy_event_repo import SqlAlchemyEventRepository
from tests.relay.test_repos.base_test_repo import EventRepoTestBase


class TestSqlalchemy(EventRepoTestBase):

    @pytest.fixture(scope="class")
    def session_maker(self, ):
        filename = "test.db"
        yield set_up_session_maker(f"sqlite:///{filename}", f"sqlite+aiosqlite:///{filename}")
        os.remove(f"{filename}")

    @pytest_asyncio.fixture()
    async def repo(self, session_maker):
        yield SqlAlchemyEventRepository(session_maker)

        await self.tables_cleanup(session_maker)

    async def tables_cleanup(self, session_maker):
        async with session_maker() as s:
            for table in reversed(mapper_registry.metadata.sorted_tables):
                await s.execute(table.delete())
            await s.commit()
