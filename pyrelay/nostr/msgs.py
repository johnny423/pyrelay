from typing import Any, Optional

import attr

from pyrelay.nostr.event import EventId, EventKind, NostrDataType, NostrEvent
from pyrelay.nostr.filters import NostrFilter


@attr.s(auto_attribs=True)
class NostrRequest(NostrDataType):
    subscription_id: str
    filters: tuple[NostrFilter, ...]

    def serialize(self) -> Any:
        return [
            "REQ",
            self.subscription_id,
        ] + [_filter.serialize() for _filter in self.filters]

    @classmethod
    def deserialize(cls, *, subscription_id, filters):
        _filters = []
        for _filter in filters:
            if "kinds" in _filter:
                _filter["kinds"] = [EventKind(kind) for kind in _filter["kinds"]]

            if "#p" in _filter:
                _filter["p_tag"] = _filter.pop("#p")

            if "#e" in _filter:
                _filter["e_tag"] = _filter.pop("#e")

            _filter = NostrFilter(**_filter)
            _filters.append(_filter)
        return NostrRequest(subscription_id=subscription_id, filters=_filters)


@attr.s(auto_attribs=True)
class NostrClose(NostrDataType):
    subscription_id: str

    def serialize(self) -> Any:
        return ["CLOSE", self.subscription_id]


@attr.s(auto_attribs=True)
class NostrEventUpdate(NostrDataType):
    subscription_id: str
    event: NostrEvent

    def serialize(self) -> Any:
        _, event_serialized = self.event.serialize()
        return ["EVENT", self.subscription_id, event_serialized]

    @classmethod
    def deserialize(cls, *, subscription_id, event) -> "NostrEventUpdate":
        return NostrEventUpdate(
            subscription_id=subscription_id, event=NostrEvent.deserialize(event=event)
        )


@attr.s(auto_attribs=True)
class NostrNoticeUpdate(NostrDataType):
    message: str

    def serialize(self) -> Any:
        return ["NOTICE", self.message]


@attr.s(auto_attribs=True)
class NostrEOSE(NostrDataType):
    """
    End of Stored Events Notice
    """

    subscription_id: str

    def serialize(self) -> Any:
        return ["EOSE", self.subscription_id]


@attr.s(auto_attribs=True)
class NostrCommandResults(NostrDataType):
    """ """

    event_id: EventId
    saved: bool
    message: Optional[str] = None

    def serialize(self) -> Any:
        return ["OK", self.event_id, self.saved, self.message]

    @classmethod
    def deserialize(cls, *, event_id, saved, message) -> "NostrCommandResults":
        return NostrCommandResults(event_id, saved, message)


#
# class Duplicate(NostrCommandResults):
#     reason = "duplicate"
#     saved = True
#
#
# # Should be exceptions?
# class Blocked(NostrCommandResults):
#     reason = "blocked"
#     saved = False
#
#
# class Invalid(NostrCommandResults):
#     reason = "invalid"
#     saved = False
#
#
# class Pow(NostrCommandResults):
#     reason = "pow"
#     saved = False
#
#
# class RateLimited(NostrCommandResults):
#     reason = "rate-limited"
#     saved = False
#
#
# class Error(NostrCommandResults):
#     reason = "error"
#     saved = False
