import asyncio

import websockets

from pyrelay.nostr.serialize import loads
from pyrelay.relay.bootstrap import get_uow_factory
from pyrelay.relay.client_session import ClientSession
from pyrelay.relay.dispatcher import RelayDispatcher

dispatcher = RelayDispatcher(uow_factory=get_uow_factory())


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
