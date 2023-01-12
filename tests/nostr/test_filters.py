import pytest

from pyrelay.nostr.event import EventKind, NostrTag
from pyrelay.nostr.event_builder import EventBuilder
from pyrelay.nostr.filters import apply, NostrFilter, apply_many


@pytest.fixture(scope="module")
def event_builder():
    return EventBuilder.from_generated()


@pytest.fixture(scope="module")
def event(event_builder):
    return event_builder.create_event("content", tags=[
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
    ])


class TestApplyFilter:

    def test_empty_filter(self, event):
        assert apply(NostrFilter.empty(), event)

    def test_ids_filter(self, event):
        filt = NostrFilter(ids=[event.id])
        assert apply(filt, event)

    def test_partial_ids_filter(self, event):
        filt = NostrFilter(ids=[event.id[:-10]])
        assert apply(filt, event)

    def test_no_match_ids_filter(self, event):
        no_match_id = "x" + event.id
        filt = NostrFilter(ids=[no_match_id])
        assert not apply(filt, event)

    def test_multiple_ids_filter(self, event):
        no_match_id = "x" + event.id
        filt = NostrFilter(ids=[no_match_id, event.id])
        assert apply(filt, event)

    def test_author_filter(self, event):
        filt = NostrFilter(authors=[event.pubkey])
        assert apply(filt, event)

    def test_partial_author_filter(self, event):
        filt = NostrFilter(authors=[event.pubkey[:-10]])
        assert apply(filt, event)

    def test_no_match_author_filter(self, event):
        no_match_author = "x" + event.pubkey
        filt = NostrFilter(authors=[no_match_author])
        assert not apply(filt, event)

    def test_multiple_author_filter(self, event):
        no_match_author = "x" + event.pubkey
        filt = NostrFilter(authors=[no_match_author, event.pubkey])
        assert apply(filt, event)

    def test_kind_filter(self, event):
        filt = NostrFilter(kinds=[event.kind])
        assert apply(filt, event)

    def test_no_match_kind_filter(self, event):
        kinds = list(EventKind)
        kinds.remove(event.kind)
        filt = NostrFilter(kinds=kinds)
        assert not apply(filt, event)

    def test_all_kind_filter(self, event):
        kinds = list(EventKind)
        filt = NostrFilter(kinds=kinds)
        assert apply(filt, event)

    def test_since_filter(self, event):
        filt = NostrFilter(since=event.created_at - 10)
        assert apply(filt, event)

    def test_since_exactly_filter(self, event):
        filt = NostrFilter(since=event.created_at)
        assert apply(filt, event)

    def test_not_match_since_filter(self, event):
        filt = NostrFilter(since=event.created_at + 10)
        assert not apply(filt, event)

    def test_until_filter(self, event):
        filt = NostrFilter(until=event.created_at + 10)
        assert apply(filt, event)

    def test_until_exactly_filter(self, event):
        filt = NostrFilter(until=event.created_at)
        assert not apply(filt, event)

    def test_not_match_until_filter(self, event):
        filt = NostrFilter(until=event.created_at - 10)
        assert not apply(filt, event)

    def test_p_tags_filter(self, event):
        tag, *_ = event.p_tags
        filt = NostrFilter(generic_tags={"p": [tag]})
        assert apply(filt, event)

    def test_e_tags_filter(self, event):
        tag, *_ = event.e_tags
        filt = NostrFilter(generic_tags={"e": [tag]})
        assert apply(filt, event)

    def test_no_match_e_tags_filter(self, event):
        tag, *_ = event.e_tags
        filt = NostrFilter(generic_tags={"e": [tag * 2]})
        assert not apply(filt, event)

    def test_all_filter(self, event):
        tag, *_ = event.e_tags
        filt = NostrFilter(
            ids=[event.id],
            authors=[event.pubkey + "XXX", event.pubkey],
            kinds=list(EventKind),
            since=event.created_at - 10,
            until=event.created_at + 10,
            generic_tags={"e": [tag]}
        )
        assert apply(filt, event)

    def test_all_filter_one_not_match(self, event):
        tag, *_ = event.e_tags
        filt = NostrFilter(
            ids=[event.id],
            authors=[event.pubkey + "XXX"],
            kinds=list(EventKind),
            since=event.created_at - 10,
            until=event.created_at + 10,
            generic_tags={"e": [tag]}
        )
        assert not apply(filt, event)

    def test_apply_many_no_filters(self, event):
        assert apply_many(event)

    def test_apply_many_one_filter_match(self, event):
        filt = NostrFilter(
            ids=[event.id],
            authors=[event.pubkey + "XXX", event.pubkey],
            kinds=list(EventKind),
            since=event.created_at - 10,
            until=event.created_at + 10,
        )
        assert apply_many(event, filt)

    def test_apply_many_one_filter_not_match(self, event):
        filt = NostrFilter(
            ids=[event.id],
            authors=[event.pubkey + "XXX"],
            kinds=list(EventKind),
            since=event.created_at - 10,
            until=event.created_at + 10,
        )
        assert not apply_many(event, filt)

    def test_apply_two_filters(self, event):
        filt_match = NostrFilter(
            ids=[event.id],
            authors=[event.pubkey + "XXX", event.pubkey],
            kinds=list(EventKind),
            since=event.created_at - 10,
            until=event.created_at + 10,
        )

        filt_no_match = NostrFilter(
            ids=[event.id],
            authors=[event.pubkey + "XXX"],
            kinds=list(EventKind),
            since=event.created_at - 10,
            until=event.created_at + 10,
        )
        assert apply_many(event, filt_match, filt_no_match)
        assert apply_many(event, filt_no_match, filt_match)
