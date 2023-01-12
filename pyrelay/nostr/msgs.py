import attr

from pyrelay.nostr.event import EventId, JSONValues, NostrDataType, NostrEvent
from pyrelay.nostr.filters import NostrFilter


@attr.s(auto_attribs=True)
class NostrRequest(NostrDataType):
    subscription_id: str
    filters: tuple[NostrFilter, ...]

    def serialize(self) -> JSONValues:
        return [
            "REQ",
            self.subscription_id,
        ] + [_filter.serialize() for _filter in self.filters]

    @classmethod
    def deserialize(cls, *, subscription_id, filters):
        _filters: list[NostrFilter] = []
        for _filter in filters:
            _filters.append(NostrFilter.deserialize(_filter))
        return NostrRequest(subscription_id=subscription_id, filters=_filters)


@attr.s(auto_attribs=True)
class NostrClose(NostrDataType):
    subscription_id: str

    def serialize(self) -> JSONValues:
        return ["CLOSE", self.subscription_id]


@attr.s(auto_attribs=True)
class NostrEventUpdate(NostrDataType):
    subscription_id: str
    event: NostrEvent

    def serialize(self) -> JSONValues:
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

    def serialize(self) -> JSONValues:
        return ["NOTICE", self.message]


@attr.s(auto_attribs=True)
class NostrEOSE(NostrDataType):
    """
    End of Stored Events Notice
    """

    subscription_id: str

    def serialize(self) -> JSONValues:
        return ["EOSE", self.subscription_id]


@attr.s(auto_attribs=True)
class NostrCommandResults(NostrDataType):
    """ """

    event_id: EventId
    saved: bool
    message: str = ""

    def serialize(self) -> JSONValues:
        return ["OK", self.event_id, self.saved, self.message or ""]

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
