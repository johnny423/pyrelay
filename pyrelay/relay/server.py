import asyncio
import logging

import websockets

from pyrelay.nostr.serialize import loads
from pyrelay.relay.bootstrap import get_uow_factory
from pyrelay.relay.client_session import ClientSession
from pyrelay.relay.dispatcher import RelayDispatcher

logger = logging.getLogger(__name__)
dispatcher = RelayDispatcher(uow_factory=get_uow_factory())


async def handler(websocket) -> None:
    client_session = ClientSession(websocket)
    logger.info("New connection conn_uid=%s", client_session.uid)
    try:
        while True:
            message = await websocket.recv()
            logger.info("New message from connection conn_uid=%s", client_session.uid)

            request = loads(message)
            await dispatcher.handle(client_session, request)
    except:
        logger.info("Connection error conn_uid=%s", client_session.uid, exc_info=True)
    finally:
        logger.info("connection closed conn_uid=%s", client_session.uid)
        client_session.close()


if __name__ == "__main__":
    event_loop = asyncio.get_event_loop()

    start_websocket_server = websockets.serve(handler, "", 8001)
    event_loop.run_until_complete(start_websocket_server)

    event_loop.run_forever()
