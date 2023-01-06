from typing import Any, Optional

import attr

from pynostr.nostr.event import EventId, EventKind, NostrDataType, NostrEvent, PubKey


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

    # <a list of event ids or prefixes>
    ids: Optional[list[EventId]] = None

    # <a list of pubkeys or prefixes, the pubkey of an event must be one of these>
    authors: Optional[list[PubKey]] = None

    """
    For scalar event attributes such as kind, the attribute from the event must
    be contained in the filter list
    """

    # <a list of a kind numbers>
    kinds: Optional[list[EventKind]] = None

    # Tags

    """
    For tag attributes such as #e, where an event may have multiple values,
    the event and filter condition values must have at least one item in common
    """
    # <a list of event ids that are referenced in an "e" tag>,
    e_tag: Optional[list[EventId]] = None
    # <a list of pubkeys that are referenced in a "p" tag>
    p_tag: Optional[list[PubKey]] = None

    # <a timestamp, events must be newer than this to pass>
    since: Optional[int] = None
    # <a timestamp, events must be older than this to pass>
    until: Optional[int] = None

    # <maximum number of events to be returned in the initial query>
    limit: Optional[int] = None

    @classmethod
    def empty(cls) -> "NostrFilter":
        return cls()

    def serialize(self) -> Any:
        data = self.dict()
        if "kinds" in data:
            data["kinds"] = [kind.value for kind in data["kinds"]]
        return data


def _match_any_prefix(prefixes: list[str], value: str) -> bool:
    return any(map(lambda pref: value.startswith(pref), prefixes))


def apply(filt: NostrFilter, event: NostrEvent) -> bool:
    return (
        (not filt.ids or _match_any_prefix(filt.ids, event.id))
        and (not filt.authors or _match_any_prefix(filt.authors, event.pubkey))
        and (not filt.kinds or event.kind in filt.kinds)
        and (not filt.p_tag or bool(set(filt.p_tag) & event.p_tags))
        and (not filt.e_tag or bool(set(filt.e_tag) & event.e_tags_keys))
        and (not filt.since or event.created_at >= filt.since)
        and (not filt.until or event.created_at < filt.until)
    )


def apply_many(event: NostrEvent, *filters: NostrFilter) -> bool:
    if not filters:
        return True

    return any(apply(filt, event) for filt in filters)
