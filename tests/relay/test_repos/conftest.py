import pytest

from pynostr.nostr.event import NostrTag
from pynostr.nostr.event_builder import EventBuilder


@pytest.fixture(scope="function")
def event_builder():
    return EventBuilder.from_generated()


@pytest.fixture(scope="function")
def event(event_builder):
    return event_builder.create_event("content", tags=[
        NostrTag(
            type="p",
            key="1234567123456712345671234",
            extra=["url://asdlkasdlks"],
        ),
        NostrTag(
            type="e",
            key="1234567123456712345671234",
            extra=["url://asdlkasdlks"],
        )
    ])