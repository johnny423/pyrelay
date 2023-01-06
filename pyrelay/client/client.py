from typing import Optional

from pyrelay.nostr.event import NostrDataType, NostrEvent, NostrTag
from pyrelay.nostr.event_builder import EventBuilder
from pyrelay.nostr.filters import NostrFilter
from pyrelay.nostr.msgs import NostrRequest
from pyrelay.nostr.serialize import dumps, loads


class NostrClient:
    def __init__(self, websocket) -> None:
        self.event_builder = EventBuilder.from_generated()
        self.websocket = websocket

    async def send_event(
        self, data: str, tags: Optional[list[NostrTag]] = None
    ) -> NostrEvent:
        event = self.event_builder.create_event(data, tags=tags)
        serialized_msg = dumps(event)
        await self.websocket.send(serialized_msg)
        return event

    async def receive(self) -> NostrDataType:
        data = await self.websocket.recv()
        return loads(data)

    async def register(self, subscription_id: str, *filters: NostrFilter) -> None:
        request = NostrRequest(subscription_id=subscription_id, filters=filters)
        serialized_msg = dumps(request)
        await self.websocket.send(serialized_msg)
