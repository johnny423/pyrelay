import secrets
import time
from typing import Optional

import secp256k1

from pyrelay.nostr.event import EventKind, NostrEvent, NostrTag, UnsignedNostrEvent


class EventBuilder:
    @classmethod
    def from_generated(cls) -> "EventBuilder":
        raw_secret = secrets.token_bytes(32)
        return cls(raw_secret)

    def __init__(self, raw_secret: bytes) -> None:
        self.raw_secret = raw_secret
        self.public_key_raw = secp256k1.PrivateKey(raw_secret).pubkey.serialize()[1:]

    @property
    def pub_key(self) -> str:
        return self.public_key_raw.hex()

    def create_event(
        self,
        content: str,
        kind: EventKind = EventKind.TextNote,  # type: ignore
        tags: Optional[list[NostrTag]] = None,
        created_at: Optional[int] = None,
    ) -> NostrEvent:
        if not created_at:
            created_at = int(time.time())

        if not tags:
            tags = []

        return UnsignedNostrEvent(
            pubkey=self.pub_key,
            created_at=created_at,
            kind=kind,
            tags=tags,
            content=content,
        ).sign(self.raw_secret.hex())
