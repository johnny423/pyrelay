from typing import Collection

from pyrelay.nostr.event import EventId, NostrEvent
from pyrelay.nostr.filters import NostrFilter, apply
from pyrelay.relay.relay_service import EventsRepository


class InMemoryEventsRepository(EventsRepository):
    def __init__(self) -> None:
        self.data: dict[EventId, NostrEvent] = {}

    async def delete(self, event_ids: Collection[EventId]) -> None:
        for event_id in event_ids:
            self.data.pop(event_id, None)

    async def add(self, event: NostrEvent) -> None:
        if event.id not in self.data:
            self.data[event.id] = event

    async def query(self, *filters: NostrFilter) -> Collection[NostrEvent]:
        if not filters:
            return list(self.data.values())

        matched: dict[EventId, NostrEvent] = {}
        limits: list[int] = []
        for _filter in filters:
            events = {
                event_id: event
                for event_id, event in self.data.items()
                if apply(_filter, event)
            }
            matched |= events

            if _filter.limit:
                limits.append(_filter.limit)

        response: list[NostrEvent] = sorted(
            matched.values(), key=lambda event: event.created_at
        )
        if limits:
            limit = max(limits)
            response = response[-limit:]

        return response
