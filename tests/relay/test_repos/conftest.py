import pytest

from pyrelay.nostr.event_builder import EventBuilder


@pytest.fixture(scope="function")
def event_builder():
    return EventBuilder.from_generated()

