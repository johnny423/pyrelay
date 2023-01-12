import enum
import json
from hashlib import sha256
from typing import Any, Collection, Mapping, Self, TypeAlias

import attr
import secp256k1

JSONValues: TypeAlias = (
    Mapping[str, "JSONValues"]
    | Collection["JSONValues"]
    | str
    | int
    | float
    | bool
    | None
)

EventId: TypeAlias = str  # <32-bytes sha256 of the the serialized event data>
PubKey: TypeAlias = str  # <32-bytes hex-encoded public key of the event creator>,
URL: TypeAlias = str

KINDS: dict[str, range | int] = {
    "Metadata": 0,  # nip  1,5
    "TextNote": 1,  # nip  1
    "RecommendRelay": 2,  # nip  1
    "ContactList": 3,  # nip 2
    "EncryptedDirectMessage": 4,  # nip 4
    "EventDeletion": 5,  # nip 9
    "Repost": 6,  # nip 18
    "Reaction": 7,  # nip 25
    # Channels
    "ChannelCreation": 40,  # nip 28
    "ChannelMetadata": 41,  # nip 28
    "ChannelMessage": 42,  # nip 28
    "ChannelHideMessage": 43,  # nip 28
    "ChannelMuteUser": 44,  # nip 28
    # Reserved
    "Replaceable": range(10000, 19999),
    "Ephemeral": range(20000, 29999),
}


def range_dict(d: dict[str, range | int]) -> dict[str, int]:
    new: dict[str, int] = {}
    for key, value in d.items():
        if isinstance(value, range):
            new |= {f"{key}_{v}": v for v in value}
        else:
            new[key] = value

    return new


EventKind = enum.IntEnum("EventKind", range_dict(KINDS))  # type: ignore


def filter_none(attribute: attr.Attribute, value: Any) -> bool:
    return value is not None


@attr.s(auto_attribs=True)
class NostrDataType:
    def serialize(self) -> JSONValues:
        """
        Each datatype should be able to covert into object that can be jsonify
        """

    @classmethod
    def deserialize(cls, **kwargs) -> Self:  # type: ignore
        """
        Each datatype should be able to loaded data into the relevant object
        """
        return cls(**kwargs)

    def dict(self) -> dict:
        return attr.asdict(self, filter=filter_none)


@attr.s(auto_attribs=True)
class NostrTag(NostrDataType):
    type: str
    key: str
    extra: list[str]

    def serialize(self) -> JSONValues:
        return [self.type, self.key] + (self.extra or [])

    def __iter__(self):
        return iter(self.serialize())


def sign_event_id(event_id: EventId, private_key_hex: str) -> str:
    private_key = secp256k1.PrivateKey(bytes.fromhex(private_key_hex))
    sig = private_key.schnorr_sign(bytes.fromhex(event_id), bip340tag=None, raw=True)
    return sig.hex()


def calc_event_id(
    public_key: PubKey, created_at: int, kind_number: int, tags: list, content: str
) -> str:
    data = [0, public_key, created_at, kind_number, tags, content]
    data_str = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    return sha256(data_str.encode("UTF-8")).hexdigest()


def verify(event_id: str, pubkey: str, sig: str) -> bool:
    pub_key = secp256k1.PublicKey(
        bytes.fromhex("02" + pubkey), True
    )  # add 02 for schnorr (bip340)
    return pub_key.schnorr_verify(
        bytes.fromhex(event_id), bytes.fromhex(sig), None, raw=True
    )


@attr.s(auto_attribs=True)
class BaseNostrEvent(NostrDataType):
    pubkey: PubKey  # <32-bytes hex-encoded public key of the event creator>,
    created_at: int  # <unix timestamp in seconds>,
    kind: EventKind  # <integer>,
    tags: list[NostrTag]
    content: str  # <arbitrary string>

    def calc_id(self) -> str:
        return calc_event_id(
            public_key=self.pubkey,
            created_at=self.created_at,
            kind_number=self.kind,
            tags=[tag.serialize() for tag in self.tags],
            content=self.content,
        )

    def get_tags_keys(self, tag_type: str) -> set[str]:
        return set(tag.key for tag in self.tags if tag.type == tag_type)

    @property
    def e_tags(self) -> set[str]:
        return self.get_tags_keys("e")

    @property
    def p_tags(self) -> set[str]:
        return self.get_tags_keys("p")


@attr.s(auto_attribs=True)
class NostrEvent(BaseNostrEvent):
    # <32-bytes sha256 of the the serialized event data>
    id: EventId

    # <64-bytes signature of the sha256 hash of the serialized event data, which is
    # the same as the "id" field>
    sig: str

    def verify(self) -> bool:
        return verify(event_id=self.calc_id(), pubkey=self.pubkey, sig=self.sig)

    def serialize(self) -> JSONValues:
        msg = self.dict()
        return ["EVENT", msg]

    @classmethod
    def deserialize(cls, *, event: dict[str, Any]) -> "NostrEvent":
        event["tags"] = [
            NostrTag(type=tag_type, key=key, extra=extra)
            for tag_type, key, *extra in event["tags"]
        ]
        event["kind"] = EventKind(event["kind"])
        return NostrEvent(**event)

    def dict(self) -> dict[str, Any]:
        msg = super(NostrEvent, self).dict()
        msg["tags"] = [tag.serialize() for tag in self.tags]
        msg["kind"] = self.kind
        return msg


@attr.s(auto_attribs=True)
class UnsignedNostrEvent(BaseNostrEvent):
    def sign(self, private_key_hex: str) -> NostrEvent:
        event_id = self.calc_id()
        return NostrEvent(
            id=event_id,
            pubkey=self.pubkey,
            created_at=self.created_at,
            kind=self.kind,
            tags=self.tags,
            content=self.content,
            sig=sign_event_id(event_id, private_key_hex),
        )
