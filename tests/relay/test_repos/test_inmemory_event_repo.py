import pytest

from pyrelay.relay.repos.in_memory_event_repo import InMemoryEventsRepository

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
class TestInMemory(EventRepoTestBase):
    @pytest.fixture(scope="module")
    def repo(self):
        return InMemoryEventsRepository()



class TestSqlAlchemyEventRepoNoFilters(TestInMemory, EventRepoNoFilters):
    ...


class TestSqlAlchemyEventRepoIdsFilters(TestInMemory, EventRepoIdsFilters):
    ...


class TestSqlAlchemyEventRepoAuthorsFilters(
    TestInMemory, EventRepoAuthorsFilters
):
    ...


class TestSqlAlchemyEventRepoKindsFilters(TestInMemory, EventRepoKindsFilters):
    ...


class TestSqlAlchemyEventRepoTimesFilters(TestInMemory, EventRepoTimesFilters):
    ...


class TestSqlAlchemyEventRepoTagsFilters(TestInMemory, EventRepoTagsFilters):
    ...


class TestSqlAlchemyEventRepoAllFilters(TestInMemory, EventRepoAllFilters):
    ...


class TestSqlAlchemyEventRepoEventSave(TestInMemory, EventRepoEventSave):
    ...
