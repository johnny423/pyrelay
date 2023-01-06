import asyncio
import logging

import websockets

from pyrelay.client.client import NostrClient
from pyrelay.nostr.filters import NostrFilter

logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger("WATCHER CLIENT")


async def watcher() -> None:
    async with websockets.connect("ws://localhost:8001") as websocket:
        client = NostrClient(websocket)
        _filter1 = NostrFilter.empty()
        _filter1.authors = ["576bfe0fe55a84c"]
        _filter1.limit = 1000

        _filter2 = NostrFilter.empty()
        _filter2.authors = ["b483b3e7c93c4d7aca712a0f81e65d9"]

        _filter3 = NostrFilter.empty()
        _filter3.authors = ["8fb210904b67151e738f7"]

        await client.register("ididididi")  # , _filter1, _filter2, _filter3)
        while True:
            msg = await client.receive()
            logger.info("got %s", msg)


if __name__ == "__main__":
    asyncio.run(watcher())
