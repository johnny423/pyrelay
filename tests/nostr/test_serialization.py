import pytest
from hypothesis import strategies as s, given

from pyrelay.nostr.event_builder import EventBuilder
from pyrelay.nostr.filters import NostrFilter
from pyrelay.nostr.msgs import (
    NostrEventUpdate,
    NostrRequest,
    NostrClose,
    NostrNoticeUpdate, NostrEOSE, NostrCommandResults,
)
from pyrelay.nostr.serialize import dumps, loads
from tests.strategies import free_text, msg_kind, timestamp, partial_hex32, hex32, non_negative, tags


@pytest.fixture(scope="module")
def event_builder():
    return EventBuilder.from_generated()


@given(
    content=free_text,
    kind=msg_kind,
    created_at=timestamp,
)
def test_serialize_event(event_builder, content, kind, created_at):
    data = event_builder.create_event(content, kind, created_at=created_at)
    assert loads(dumps(data)) == data


@given(
    content=free_text,
    kind=msg_kind,
    created_at=timestamp,
    subscription_id=free_text,
    tags=tags
)
def test_serialize_event_update(
        event_builder, content, kind, created_at, subscription_id, tags
):
    event = event_builder.create_event(content=content, kind=kind, tags=tags, created_at=created_at)
    data = NostrEventUpdate(subscription_id=subscription_id, event=event)
    assert loads(dumps(data)) == data


@given(
    subscription_id=free_text,
    amount=s.integers(min_value=0, max_value=10),
    ids=s.lists(partial_hex32 | hex32),
    authors=s.lists(partial_hex32 | hex32),
    kinds=s.lists(msg_kind),
    e_tags=s.lists(hex32),
    p_tags=s.lists(hex32),
    since=timestamp,
    until=timestamp,
    limit=s.none() | non_negative

)
def test_serialize_request(
        subscription_id,
        amount,
        ids,
        authors,
        kinds,
        e_tags,
        p_tags,
        since,
        until,
        limit,
):
    tags = {}
    if e_tags:
        tags["e"] = e_tags
    if p_tags:
        tags["p"] = p_tags

    filters = [
        NostrFilter(
            ids=ids,
            authors=authors,
            kinds=kinds,
            generic_tags=tags or None,
            since=since,
            until=until,
            limit=limit,
        )
        for _ in range(amount)
    ]
    data = NostrRequest(
        subscription_id,
        filters=filters,

    )
    assert loads(dumps(data)) == data


@given(subscription_id=free_text)
def test_serialize_close(subscription_id):
    data = NostrClose(subscription_id)
    assert loads(dumps(data)) == data


@given(subscription_id=free_text)
def test_serialize_eose(subscription_id):
    data = NostrEOSE(subscription_id)
    assert loads(dumps(data)) == data


@given(message=free_text)
def test_serialize_notice_update(message):
    data = NostrNoticeUpdate(message)
    assert loads(dumps(data)) == data


@given(
    event_id=hex32,
    saved=s.booleans(),
    message=free_text,
)
def test_serialize_command_results(
        event_id,
        saved,
        message,
):
    data = NostrCommandResults(
        event_id=event_id,
        saved=saved,
        message=message,
    )
    assert loads(dumps(data)) == data


def test_loads_failed_json():
    with pytest.raises(ValueError):
        loads("asdasd")


def test_loads_failed():
    with pytest.raises(ValueError):
        loads('["asdasd"]')
