from pyrelay.nostr.event import NostrDataType, NostrEvent
from pyrelay.nostr.msgs import NostrClose, NostrRequest
from pyrelay.relay.client_session import ClientSession
from pyrelay.relay.handlers.event_handler import send_event
from pyrelay.relay.handlers.subscribe_handler import subscribe
from pyrelay.relay.handlers.unsubscribe_handler import unsubscribe
from pyrelay.relay.relay_service import UOW, EventsRepository, Subscriptions


class RelayDispatcher:
    def __init__(
        self, event_repository: EventsRepository, subscriptions: Subscriptions
    ):
        self.subscriptions = subscriptions
        self.event_repository = event_repository

    async def handle(
        self, client_session: ClientSession, message: NostrDataType
    ) -> None:
        """
        Route the different msgs
        """
        uow = UOW(self.event_repository, self.subscriptions)
        match message:
            case NostrEvent() as event:
                await send_event(uow, client_session, event)

            case NostrRequest() as request:
                await subscribe(uow, client_session, request)

            case NostrClose() as close:
                await unsubscribe(uow, close)

            case other:
                raise TypeError(f"can't handle request, got {other}")
