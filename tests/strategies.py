import string

from hypothesis import strategies as s
from hypothesis.strategies import composite

from pyrelay.nostr.event import EventKind, NostrTag
from pyrelay.nostr.event_builder import EventBuilder

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


@composite
def generate_event(draw):
    event_builder = EventBuilder.from_generated()
    content = draw(free_text)
    ttags = draw(tags)
    return event_builder.create_event(content, tags=ttags)


@composite
def generate_event_with_tags(draw):
    event_builder = EventBuilder.from_generated()
    content = draw(free_text)

    return event_builder.create_event(
        content,
        tags=[
            NostrTag(
                type="p",
                key="1234567123456712345671234",
                extra=["url://asdlkasdlks"],
            ),
            NostrTag(
                type="e",
                key="1234567123456712345671234",
                extra=["url://asdlkasdlks"],
            )
        ]
    )


event = generate_event()
events = s.lists(event, min_size=2, max_size=30)
event_with_tags = generate_event_with_tags()
