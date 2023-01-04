import string

from hypothesis import strategies as s

from pynostr.nostr.event import EventKind, NostrTag

free_text = s.text()
msg_kind = s.from_type(EventKind)
timestamp = s.none() | s.datetimes().map(lambda dt: dt.timestamp()).filter(
    lambda ts: ts > 0
)

hex_text = s.text(alphabet=string.hexdigits)
hex32 = s.text(alphabet=string.hexdigits, min_size=64, max_size=64)
partial_hex32 = s.text(alphabet=string.hexdigits, min_size=1, max_size=64)
non_negative = s.integers(min_value=0)

tags = s.lists(s.from_type(NostrTag))  # todo: improve
