from typing import Optional, Self

import attr

from pyrelay.nostr.event import (
    EventId,
    EventKind,
    JSONValues,
    NostrDataType,
    NostrEvent,
    PubKey,
)


@attr.s(auto_attribs=True)
class NostrFilter(NostrDataType):
    """
    The ids and authors lists contain lowercase hexadecimal strings,
    which may either be an exact 64-character match, or a prefix of the event value.
    A prefix match is when the filter string is an exact string prefix of the event
    value. The use of prefixes allows for more compact filt where a large number of
    values are queried, and can provide some privacy for clients that may not want
    to disclose the exact authors or events they are searching for.
    """

    ids: Optional[list[EventId]] = None  # <a list of event ids or prefixes>
    authors: Optional[list[PubKey]] = None  # <a list of pubkeys or prefixes>

    # For scalar event attributes such as kind, the attribute from the event must
    # be contained in the filter list
    kinds: Optional[list[EventKind]] = None  # <a list of a kind numbers>

    # Timestamps
    since: Optional[int] = None  # <a timestamp, events must be newer than this to pass>
    until: Optional[int] = None  # <a timestamp, events must be older than this to pass>

    # <maximum number of events to be returned in the initial query>
    limit: Optional[int] = None

    # Tags
    # For tag attributes such as #e, where an event may have multiple values,
    # the event and filter condition values must have at least one item in common
    # NIP-12 extend the regular #e and #p tags filters with any one letter tags filters
    # https://github.com/nostr-protocol/nips/blob/master/12.md
    generic_tags: Optional[dict[str, list[str]]] = None

    @classmethod
    def empty(cls) -> "NostrFilter":
        return cls()

    @classmethod
    def deserialize(cls, kwargs) -> Self:
        if "kinds" in kwargs:
            kwargs["kinds"] = [EventKind(kind) for kind in kwargs["kinds"]]

        generic_tags = {}
        kwargz = {}
        for key, values in kwargs.items():
            match list(key):
                case ["#", k]:  # only supporting one letter filter
                    generic_tags[k] = values
                case _:
                    kwargz[key] = values

        if generic_tags:
            kwargz["generic_tags"] = generic_tags

        return NostrFilter(**kwargz)

    def serialize(self) -> JSONValues:
        data = self.dict()
        if "kinds" in data:
            data["kinds"] = [kind for kind in data["kinds"]]

        if "generic_tags" in data:
            for key, values in data.pop("generic_tags").items():
                data[f"#{key}"] = values

        return data


def _match_any_prefix(prefixes: list[str], value: str) -> bool:
    return any(map(lambda pref: value.startswith(pref), prefixes))


def apply(filt: NostrFilter, event: NostrEvent) -> bool:
    return (
        (not filt.ids or _match_any_prefix(filt.ids, event.id))
        and (not filt.authors or _match_any_prefix(filt.authors, event.pubkey))
        and (not filt.kinds or event.kind in filt.kinds)
        and (not filt.since or event.created_at >= filt.since)
        and (not filt.until or event.created_at < filt.until)
        and (
            not filt.generic_tags
            or all(
                bool(set(values) & event.get_tags_keys(k))
                for k, values in filt.generic_tags.items()
            )
        )
    )


def apply_many(event: NostrEvent, *filters: NostrFilter) -> bool:
    if not filters:
        return True

    return any(apply(filt, event) for filt in filters)
