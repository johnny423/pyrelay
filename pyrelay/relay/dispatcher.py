import logging
from typing import Callable

from pyrelay.nostr.event import NostrDataType, NostrEvent
from pyrelay.nostr.msgs import NostrClose, NostrRequest
from pyrelay.relay.client_session import ClientSession
from pyrelay.relay.handlers.send_event_handler import send_event
from pyrelay.relay.handlers.subscribe_handler import subscribe
from pyrelay.relay.handlers.unsubscribe_handler import unsubscribe
from pyrelay.relay.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class RelayDispatcher:
    def __init__(self, uow_factory: Callable[[], UnitOfWork]):
        self.uow_factory = uow_factory

    async def handle(
            self, client_session: ClientSession, message: NostrDataType
    ) -> None:
        """
        Route different msgs
        """
        uow = self.uow_factory()
        match message:
            case NostrEvent() as event:
                logger.info("Got event=%s conn_uid=%s", event, client_session.uid)
                await send_event(uow, client_session, event)

            case NostrRequest() as request:
                logger.info("Got request=%s conn_uid=%s", request, client_session.uid)
                await subscribe(uow, client_session, request)

            case NostrClose() as close:
                logger.info("Got close=%s conn_uid=%s", close, client_session.uid)
                await unsubscribe(uow, close)

            case other:
                raise TypeError(f"can't handle request, got {other}")
