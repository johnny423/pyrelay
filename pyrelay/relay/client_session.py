import uuid
from typing import Any, Callable, Optional

from pyrelay.nostr.event import NostrDataType
from pyrelay.nostr.serialize import dumps


class BaseClientSession:
    def __init__(self) -> None:
        self._closed = False
        self._on_close: Optional[Callable] = None

    @property
    def on_close(self) -> Callable[[], Any]:
        if self._on_close:
            return self._on_close

        return lambda: None

    @on_close.setter
    def on_close(self, func: Callable[[], None]) -> None:
        self._on_close = func

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            self.on_close()


class ClientSession(BaseClientSession):
    def __init__(self, websocket) -> None:
        super(ClientSession, self).__init__()
        self.websocket = websocket
        self.uid = uuid.uuid4()

    async def send(self, msg: NostrDataType) -> None:
        if self._closed:
            return

        await self.websocket.send(dumps(msg))
