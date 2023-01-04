import logging
from abc import ABC, abstractmethod
from collections import UserDict

import attr

from pynostr.nostr.event import NostrDataType, NostrEvent
from pynostr.nostr.filters import NostrFilter, apply_many
from pynostr.nostr.requests import NostrClose, NostrEventUpdate, NostrRequest
from pynostr.relay.client_session import ClientSession

logger = logging.getLogger(__name__)


class EventsRepository(ABC):
    @abstractmethod
    async def add(self, event: NostrEvent) -> None:
        """
        Saves new event
        """

    @abstractmethod
    async def query(self, *filters: NostrFilter) -> list[NostrEvent]:
        """
        Fetch stored events that match one of the filters
        """


@attr.s(auto_attribs=True)
class Subscription:
    """
    Single client register for updates
    """

    request: NostrRequest
    client_session: ClientSession

    async def update(self, event: NostrEvent) -> None:
        if apply_many(event, *self.request.filters):
            update = NostrEventUpdate(
                subscription_id=self.request.subscription_id, event=event
            )
            await self.client_session.send_event(update)


class Subscriptions(UserDict[str, Subscription]):
    def subscribe(self, request: NostrRequest, client: ClientSession) -> None:
        self[request.subscription_id] = Subscription(request, client)
        client.on_close = lambda: self.pop(request.subscription_id, None)

    def unsubscribe(self, subscription_id: str) -> None:
        del self[subscription_id]

    async def broadcast(self, event: NostrEvent) -> None:
        for subscription in self.values():
            await subscription.update(event)


class RelayService:
    def __init__(
        self, event_repository: EventsRepository, subscriptions: Subscriptions
    ):
        self.subscriptions = subscriptions
        self.event_repository = event_repository

    async def handle(
        self, client_session: ClientSession, message: NostrDataType
    ) -> None:
        match message:
            case NostrEvent() as event:
                await self.send_event(event)

            case NostrRequest() as request:
                await self.subscribe(client_session, request)

            case NostrClose() as close:
                await self.unsubscribe(close)

            case other:
                raise TypeError(f"can't handle request, got {other}")

    async def send_event(self, event: NostrEvent) -> None:
        await self.event_repository.add(event)
        await self.subscriptions.broadcast(event)

    async def subscribe(self, client: ClientSession, request: NostrRequest) -> None:
        events = await self.event_repository.query(*request.filters)
        for event in events:
            update = NostrEventUpdate(
                subscription_id=request.subscription_id, event=event
            )
            await client.send_event(update)

        self.subscriptions.subscribe(request, client)

    async def unsubscribe(self, close: NostrClose) -> None:
        self.subscriptions.unsubscribe(close.subscription_id)
