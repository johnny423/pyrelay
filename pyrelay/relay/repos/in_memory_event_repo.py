from pyrelay.nostr.event import EventId, NostrEvent
from pyrelay.nostr.filters import NostrFilter, apply
from pyrelay.relay.relay_service import EventsRepository


class InMemoryEventsRepository(EventsRepository):
    def __init__(self) -> None:
        self.data: list[NostrEvent] = []

    async def add(self, event: NostrEvent) -> None:
        self.data.append(event)

    async def query(self, *filters: NostrFilter) -> list[NostrEvent]:
        if not filters:
            return self.data

        matched: dict[EventId, NostrEvent] = {}
        limits: list[int] = []
        for _filter in filters:
            events = {event.id: event for event in self.data if apply(_filter, event)}
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
