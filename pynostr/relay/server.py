import asyncio
import logging

import websockets

from pynostr.nostr.serialize import loads
from pynostr.relay.bootstrap import set_up_session_maker
from pynostr.relay.client_session import ClientSession
from pynostr.relay.relay_service import RelayService, Subscriptions
from pynostr.relay.repos.sqlalchemy_event_repo import SqlAlchemyEventRepository

session_maker = set_up_session_maker()
repo = SqlAlchemyEventRepository(session_maker)
subscriptions = Subscriptions()
service = RelayService(repo, subscriptions)
logging.basicConfig(level=logging.INFO)


# Implementation
# todo: dependency injection
# todo: try using broadcast (?)


async def handler(websocket) -> None:
    client_session = ClientSession(websocket)
    try:
        while True:
            message = await websocket.recv()
            message = loads(message)
            await service.handle(client_session, message)
    finally:
        client_session.close()


async def main() -> None:
    async with websockets.serve(ws_handler=handler, host="", port=8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
