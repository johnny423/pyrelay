import asyncio

import websockets

from pyrelay.nostr.serialize import loads
from pyrelay.relay.bootstrap import set_up_session_maker
from pyrelay.relay.client_session import ClientSession
from pyrelay.relay.dispatcher import RelayDispatcher
from pyrelay.relay.relay_service import Subscriptions
from pyrelay.relay.repos.sqlalchemy_event_repo import SqlAlchemyEventRepository

session_maker = set_up_session_maker()
repo = SqlAlchemyEventRepository(session_maker)
subscriptions = Subscriptions()
dispatcher = RelayDispatcher(repo, subscriptions)


async def handler(websocket) -> None:
    client_session = ClientSession(websocket)
    try:
        while True:
            message = await websocket.recv()
            request = loads(message)
            await dispatcher.handle(client_session, request)
    finally:
        client_session.close()


async def main() -> None:
    async with websockets.serve(ws_handler=handler, host="", port=8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
