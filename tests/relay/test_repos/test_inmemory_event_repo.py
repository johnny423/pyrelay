import pytest

from pyrelay.relay.bootstrap import get_uow_factory
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
    def uow(self):
        return get_uow_factory(in_memory=True)()


class TestInMemoryEventRepoNoFilters(TestInMemory, EventRepoNoFilters):
    ...


class TestInMemoryEventRepoIdsFilters(TestInMemory, EventRepoIdsFilters):
    ...


class TestInMemoryEventRepoAuthorsFilters(
    TestInMemory, EventRepoAuthorsFilters
):
    ...


class TestInMemoryEventRepoKindsFilters(TestInMemory, EventRepoKindsFilters):
    ...


class TestInMemoryEventRepoTimesFilters(TestInMemory, EventRepoTimesFilters):
    ...


class TestInMemoryEventRepoTagsFilters(TestInMemory, EventRepoTagsFilters):
    ...


class TestInMemoryEventRepoAllFilters(TestInMemory, EventRepoAllFilters):
    ...


class TestInMemoryEventRepoEventSave(TestInMemory, EventRepoEventSave):
    ...
