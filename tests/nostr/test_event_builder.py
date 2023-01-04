import pytest
from hypothesis import given

from pynostr.nostr.event_builder import EventBuilder
from tests.strategies import free_text, msg_kind, timestamp


@pytest.fixture(scope="module")
def event_builder():
    return EventBuilder.from_generated()


# todo: tests with tags
@given(
    content=free_text,
    kind=msg_kind,
    created_at=timestamp,
)
def test_serialize_event_update(
        event_builder, content, kind, created_at
):
    event = event_builder.create_event(content=content, kind=kind, tags=None, created_at=created_at)
    assert event.verify()
