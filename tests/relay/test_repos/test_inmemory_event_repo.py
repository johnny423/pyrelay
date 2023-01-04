import pytest

from pynostr.relay.repos.in_memory_event_repo import InMemoryEventsRepository
from tests.relay.test_repos.base_test_repo import EventRepoTestBase


class TestInMemory(EventRepoTestBase):
    @pytest.fixture()
    def repo(self):
        return InMemoryEventsRepository()
