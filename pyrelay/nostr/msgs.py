from typing import Any

import attr

from pyrelay.nostr.event import NostrDataType, NostrEvent
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
