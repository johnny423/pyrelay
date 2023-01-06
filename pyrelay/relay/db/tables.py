from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    PickleType,
    String,
    Table,
)
from sqlalchemy.orm import registry, relationship

from pyrelay.nostr.event import EventKind, NostrEvent, NostrTag

mapper_registry = registry()

event = Table(
    "event",
    mapper_registry.metadata,
    Column("db_id", Integer, primary_key=True, autoincrement=True),
    Column("id", String),
    Column("pubkey", String, nullable=False, index=True),
    Column("kind", Enum(EventKind), nullable=False, index=True),
    Column("created_at", Integer, index=True),
    Column("content", String, nullable=False),
    Column("sig", String, nullable=False),
    Column("deleted_at", DateTime, nullable=True),
)

tag = Table(
    "tag",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("event_id", String, ForeignKey("event.id")),
    Column("type", String),
    Column("key", String),
    Column("extra", PickleType),
)


def init_mapper() -> None:
    mapper_registry.map_imperatively(
        NostrEvent,
        event,
        properties={
            "tags": relationship(
                NostrTag,
                uselist=True,
                lazy="joined",
                backref="event",
                order_by=tag.c.id,
            )
        },
    )

    mapper_registry.map_imperatively(NostrTag, tag)
