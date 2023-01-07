import logging
from abc import ABC, abstractmethod
from collections import UserDict
from typing import Collection

import attr

from pyrelay.nostr.event import EventId, NostrEvent
from pyrelay.nostr.filters import NostrFilter, apply_many
from pyrelay.nostr.msgs import NostrEventUpdate, NostrRequest
from pyrelay.relay.client_session import ClientSession

logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger("RELAY")


class EventsRepository(ABC):
    @abstractmethod
    async def add(self, event: NostrEvent) -> None:
        """
        Saves new event
        """

    @abstractmethod
    async def query(self, *filters: NostrFilter) -> Collection[NostrEvent]:
        """
        Fetch stored events that match one of the filters
        """

    async def delete(self, event_ids: Collection[EventId]) -> None:
        """
        Mark event ids as deleted
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
            await self.client_session.send(update)


class Subscriptions(UserDict[str, Subscription]):
    def subscribe(self, request: NostrRequest, client: ClientSession) -> None:
        self[request.subscription_id] = Subscription(request, client)
        client.on_close = lambda: self.pop(request.subscription_id, None)

    def unsubscribe(self, subscription_id: str) -> None:
        try:
            del self[subscription_id]
        except KeyError:
            logger.warning(
                "Trying to unsubscribe id=%s but it doesn't exists", subscription_id
            )

    async def broadcast(self, event: NostrEvent) -> None:
        for subscription in self.values():
            await subscription.update(event)
