import json
from typing import Any

from pynostr.nostr.event import EventKind, NostrDataType, NostrEvent, NostrTag
from pynostr.nostr.filters import NostrFilter
from pynostr.nostr.msgs import (
    NostrClose,
    NostrEOSE,
    NostrEventUpdate,
    NostrNoticeUpdate,
    NostrRequest,
)


def loads(message: str) -> NostrDataType:
    message = json.loads(message)
    match message:
        case ["EVENT", event]:
            return _parse_event(event)

        case ["EVENT", subscription_id, event]:
            return NostrEventUpdate(
                subscription_id=subscription_id, event=_parse_event(event)
            )

        case ["REQ", subscription_id, *filters]:
            return _parse_nostr_request(filters, subscription_id)

        case ["CLOSE", subscription_id]:
            return NostrClose(subscription_id=subscription_id)

        case ["NOTICE", msg]:
            return NostrNoticeUpdate(message=msg)

        case ["EOSE", subscription_id]:
            return NostrEOSE(subscription_id=subscription_id)

        case other:
            raise ValueError(f"can't loads {other}")


def _parse_nostr_request(filters, subscription_id):
    _filters = []
    for _filter in filters:
        if "kinds" in _filter:
            _filter["kinds"] = [EventKind(kind) for kind in _filter["kinds"]]

        _filter = NostrFilter(**_filter)
        _filters.append(_filter)
    return NostrRequest(subscription_id=subscription_id, filters=_filters)


def _parse_event(event: dict[str, Any]) -> NostrEvent:
    event["tags"] = [
        NostrTag(type=tag_type, key=key, extra=extra)
        for tag_type, key, *extra in event["tags"]
    ]
    event["kind"] = EventKind(event["kind"])
    return NostrEvent(**event)


def dumps(data: NostrDataType) -> str:
    msg = data.serialize()
    return json.dumps(msg)
