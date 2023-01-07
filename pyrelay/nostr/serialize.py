import json

from pyrelay.nostr.event import NostrDataType, NostrEvent
from pyrelay.nostr.msgs import (
    NostrClose,
    NostrCommandResults,
    NostrEOSE,
    NostrEventUpdate,
    NostrNoticeUpdate,
    NostrRequest,
)


def loads(message: str) -> NostrDataType:
    message = json.loads(message)
    match message:
        case ["EVENT", event]:
            return NostrEvent.deserialize(event=event)

        case ["EVENT", subscription_id, event]:
            return NostrEventUpdate.deserialize(
                subscription_id=subscription_id, event=event
            )

        case ["REQ", subscription_id, *filters]:
            return NostrRequest.deserialize(
                subscription_id=subscription_id,
                filters=filters,
            )

        case ["CLOSE", subscription_id]:
            return NostrClose.deserialize(subscription_id=subscription_id)

        case ["NOTICE", msg]:
            return NostrNoticeUpdate.deserialize(message=msg)

        case ["EOSE", subscription_id]:
            return NostrEOSE.deserialize(subscription_id=subscription_id)

        case ["OK", event_id, saved, msg]:
            return NostrCommandResults.deserialize(
                event_id=event_id, saved=saved, message=msg
            )

        case other:
            raise ValueError(f"can't loads {other}")


def dumps(data: NostrDataType) -> str:
    msg = data.serialize()
    return json.dumps(msg)
