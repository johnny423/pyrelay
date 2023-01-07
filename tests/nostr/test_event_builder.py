import pytest
from hypothesis import given

from pyrelay.nostr.event_builder import EventBuilder
from tests.strategies import free_text, msg_kind, timestamp, tags


@pytest.fixture(scope="module")
def event_builder():
    return EventBuilder.from_generated()


@given(
    content=free_text,
    kind=msg_kind,
    created_at=timestamp,
    tags=tags,
)
def test_serialize_event_update(
        event_builder, content, kind, created_at, tags
):
    event = event_builder.create_event(content=content, kind=kind, tags=tags, created_at=created_at)
    assert event.verify()
