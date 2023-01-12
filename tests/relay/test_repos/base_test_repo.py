import pytest
from hypothesis import given, assume, settings, HealthCheck

from pyrelay.nostr.event import EventKind, NostrTag
from pyrelay.nostr.filters import NostrFilter
from tests.strategies import event, event_with_tags, events


class EventRepoTestBase:

    async def assert_apply(self, filt, event, uow):
        async with uow:
            await uow.events.add(event)

        async with uow:
            events = await (uow.events.query(*filt) if filt else uow.events.query())

        result = event.id in set(e.id for e in events)
        async with uow:
            uow.events.delete([event.id])

        return result


class EventRepoNoFilters(EventRepoTestBase):
    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_no_filter(self, event, uow):
        assert await self.assert_apply(None, event, uow)

    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_empty_filter(self, event, uow):
        filt = NostrFilter.empty()
        assert await self.assert_apply([filt], event, uow)


class EventRepoIdsFilters(EventRepoTestBase):

    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_ids_filter(self, event, uow):
        filt = NostrFilter(ids=[event.id])
        assert await self.assert_apply([filt], event, uow)

    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_partial_ids_filter(self, event, uow):
        filt = NostrFilter(ids=[event.id[:-10]])
        assert await self.assert_apply([filt], event, uow)

    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_no_match_ids_filter(self, event, uow):
        no_match_id = "x" + event.id
        filt = NostrFilter(ids=[no_match_id])
        assert not await self.assert_apply([filt], event, uow)

    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_multiple_ids_filter(self, event, uow):
        no_match_id = "x" + event.id
        filt = NostrFilter(ids=[no_match_id, event.id])
        assert await self.assert_apply([filt], event, uow)


class EventRepoAuthorsFilters(EventRepoTestBase):
    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_author_filter(self, event, uow):
        filt = NostrFilter(authors=[event.pubkey])
        assert await self.assert_apply([filt], event, uow)

    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_partial_author_filter(self, event, uow):
        filt = NostrFilter(authors=[event.pubkey[:-10]])
        assert await self.assert_apply([filt], event, uow)

    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_no_match_author_filter(self, event, uow):
        no_match_author = "x" + event.pubkey
        filt = NostrFilter(authors=[no_match_author])
        assert not await self.assert_apply([filt], event, uow)

    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_multiple_author_filter(self, event, uow):
        no_match_author = "x" + event.pubkey
        filt = NostrFilter(authors=[no_match_author, event.pubkey])
        assert await self.assert_apply([filt], event, uow)


class EventRepoKindsFilters(EventRepoTestBase):
    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_kind_filter(self, event, uow):
        filt = NostrFilter(kinds=[event.kind])
        assert await self.assert_apply([filt], event, uow)

    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_no_match_kind_filter(self, event, uow):
        kinds = list(EventKind)[:30]
        kinds.remove(event.kind)
        filt = NostrFilter(kinds=kinds)
        assert not await self.assert_apply([filt], event, uow)

    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_all_kind_filter(self, event, uow):
        kinds = list(EventKind)[:30]
        filt = NostrFilter(kinds=kinds)
        assert await self.assert_apply([filt], event, uow)


class EventRepoTimesFilters(EventRepoTestBase):
    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_since_filter(self, event, uow):
        filt = NostrFilter(since=event.created_at - 10)
        assert await self.assert_apply([filt], event, uow)

    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_since_exactly_filter(self, event, uow):
        filt = NostrFilter(since=event.created_at)
        assert await self.assert_apply([filt], event, uow)

    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_not_match_since_filter(self, event, uow):
        filt = NostrFilter(since=event.created_at + 10)
        assert not await self.assert_apply([filt], event, uow)

    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_until_filter(self, event, uow):
        filt = NostrFilter(until=event.created_at + 10)
        assert await self.assert_apply([filt], event, uow)

    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_until_exactly_filter(self, event, uow):
        filt = NostrFilter(until=event.created_at)
        assert not await self.assert_apply([filt], event, uow)

    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_not_match_until_filter(self, event, uow):
        filt = NostrFilter(until=event.created_at - 10)
        assert not await self.assert_apply([filt], event, uow)


class EventRepoTagsFilters(EventRepoTestBase):
    @pytest.mark.asyncio
    @given(event=event_with_tags)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_p_tags_filter(self, event, uow):
        assume(len(event.p_tags) > 0)
        tag, *_ = event.p_tags
        filt = NostrFilter(generic_tags={"p": [tag]},)
        assert await self.assert_apply([filt], event, uow)

    @pytest.mark.asyncio
    @given(event=event_with_tags)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_e_tags_filter(self, event, uow):
        tag, *_ = event.e_tags
        filt = NostrFilter(generic_tags={"e": [tag]},)
        assert await self.assert_apply([filt], event, uow)

    @pytest.mark.asyncio
    @given(event=event_with_tags)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_no_match_e_tags_filter(self, event, uow):
        assume(len(event.e_tags) > 0)
        tag, *_ = event.e_tags
        filt = NostrFilter(generic_tags={"e": [tag*2]},)
        assert not await self.assert_apply([filt], event, uow)


class EventRepoAllFilters(EventRepoTestBase):
    @pytest.mark.asyncio
    @given(event=event_with_tags)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_all_filter(self, event, uow):
        assume(len(event.e_tags) > 0)
        tag, *_ = event.e_tags
        filt = NostrFilter(
            ids=[event.id],
            authors=[event.pubkey + "XXX", event.pubkey],
            kinds=list(EventKind)[:30],
            since=event.created_at - 10,
            until=event.created_at + 10,
            generic_tags={"e": [tag]},
        )
        assert await self.assert_apply([filt], event, uow)

    @pytest.mark.asyncio
    @given(event=event_with_tags)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_all_filter_one_not_match(self, event, uow):
        assume(len(event.e_tags) > 0)
        tag, *_ = event.e_tags
        filt = NostrFilter(
            ids=[event.id],
            authors=[event.pubkey + "XXX"],
            kinds=list(EventKind)[:30],
            since=event.created_at - 10,
            until=event.created_at + 10,
            generic_tags={"e": [tag]},
        )
        assert not await self.assert_apply([filt], event, uow)

    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_apply_many_one_filter_match(self, event, uow):
        filt = NostrFilter(
            ids=[event.id],
            authors=[event.pubkey + "XXX", event.pubkey],
            kinds=list(EventKind)[:30],
            since=event.created_at - 10,
            until=event.created_at + 10,
        )
        assert await self.assert_apply([filt], event, uow)

    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_apply_many_one_filter_not_match(self, event, uow):
        filt = NostrFilter(
            ids=[event.id],
            authors=[event.pubkey + "XXX"],
            kinds=list(EventKind)[:30],
            since=event.created_at - 10,
            until=event.created_at + 10,
        )
        assert not await self.assert_apply([filt], event, uow)

    @pytest.mark.asyncio
    @given(event=event)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_apply_two_filters(self, event, uow):
        filt_match = NostrFilter(
            ids=[event.id],
            authors=[event.pubkey + "XXX", event.pubkey],
            kinds=list(EventKind)[:30],
            since=event.created_at - 10,
            until=event.created_at + 10,
        )

        filt_no_match = NostrFilter(
            ids=[event.id],
            authors=[event.pubkey + "XXX"],
            kinds=list(EventKind)[:30],
            since=event.created_at - 10,
            until=event.created_at + 10,
        )
        assert await self.assert_apply([filt_no_match, filt_match], event, uow)
        assert await self.assert_apply([filt_match, filt_no_match], event, uow)


class EventRepoEventSave(EventRepoTestBase):
    @pytest.mark.asyncio
    async def test_event_type_3(self, event_builder, uow):
        event = event_builder.create_event(
            "", kind=EventKind.ContactList, tags=
            [
                NostrTag("p", "91cf9..4e5ca", extra=["wss://alicerelay.com/", "alice"]),
                NostrTag("p", "14aeb..8dad4", extra=["wss://bobrelay.com/nostr", "bob"]),
                NostrTag("p", "612ae..e610f", extra=["ws://carolrelay.com/ws", "carol"]),
            ]
        )
        assert self.assert_apply(None, event, uow)

    @pytest.mark.asyncio
    @given(events=events)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, ])
    async def test_multiple_events(self, events, uow):
        event_ids = set(e.id for e in events)
        async with uow:
            for event in events:
                await uow.events.add(event)

        async with uow:
            results = await uow.events.query()

        r = set(e.id for e in results)
        assert r == event_ids

        async with uow:
            await uow.events.delete(event_ids)
