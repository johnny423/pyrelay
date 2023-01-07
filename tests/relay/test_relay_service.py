from collections import defaultdict

import pytest

from pyrelay.nostr.event import EventKind, NostrTag, NostrDataType
from pyrelay.nostr.event_builder import EventBuilder
from pyrelay.nostr.filters import NostrFilter
from pyrelay.nostr.msgs import NostrEventUpdate, NostrRequest, NostrClose, NostrEOSE
from pyrelay.relay.client_session import BaseClientSession
from pyrelay.relay.relay_service import Subscriptions
from pyrelay.relay.dispatcher import RelayDispatcher
from pyrelay.relay.repos.in_memory_event_repo import InMemoryEventsRepository
from pyrelay.relay.unit_of_work import InMemoryUOW


@pytest.fixture(scope="module")
def event_builder():
    return EventBuilder.from_generated()


class MockClientSession(BaseClientSession):
    def __init__(self):
        super(MockClientSession, self).__init__()
        self.calls = defaultdict(list)

    async def send(self, event_update: NostrDataType):
        self.calls["send_event"].append(event_update)


def get_service():
    subs = Subscriptions()
    uow = InMemoryUOW(subs)
    dispatcher = RelayDispatcher(uow)
    return dispatcher


class TestRelayService:
    @pytest.mark.asyncio
    async def test_report_and_save_events(self, event_builder):
        service = get_service()

        events = []
        for i in range(10):
            event = event_builder.create_event(f"{i}")
            events.append(event)
            client_session = MockClientSession()
            await service.handle(client_session, event)

        result = await service.uow.events.query()
        assert events == result

    @pytest.mark.asyncio
    async def test_subscribe_and_broadcast(self):
        service = get_service()

        event_builders = []
        for _ in range(10):
            event_builder = EventBuilder.from_generated()
            event_builders.append(event_builder)

        # Report events and without subscribers
        events = []
        for i, event_builder in enumerate(event_builders):
            event = event_builder.create_event(f"{i}")
            events.append(event)
            client_session = MockClientSession()
            await service.handle(client_session, event)

        # Subscribe to events and query
        clients = []
        for j, event_builder in enumerate(event_builders):
            subscribe_request = NostrRequest(
                subscription_id=f"{j}",
                filters=[NostrFilter(authors=[event_builder.pub_key])]
            )
            subscriber_client_session = MockClientSession()
            await service.handle(subscriber_client_session, subscribe_request)
            clients.append(subscriber_client_session)

        for j, client in enumerate(clients):
            calls = client.calls["send_event"]
            expected = [
                NostrEventUpdate(f"{j}", events[j]),
                NostrEOSE(f"{j}")
            ]
            assert calls == expected

        # Report events and broadcast to subscribers
        for i, event_builder in enumerate(event_builders):
            event = event_builder.create_event(f"{i * 2}")
            events.append(event)
            client_session = MockClientSession()
            await service.handle(client_session, event)

        for j, client in enumerate(clients):
            calls = client.calls["send_event"]
            expected = [
                NostrEventUpdate(f"{j}", events[j]),
                NostrEOSE(f"{j}"),
                NostrEventUpdate(f"{j}", events[j + 10]),

            ]

            assert calls == expected

        # Un-subscribe
        for j, client in enumerate(clients):
            await service.handle(client, NostrClose(f"{j}"))

        for i, event_builder in enumerate(event_builders):
            event = event_builder.create_event(f"{i * 3}")
            events.append(event)
            client_session = MockClientSession()
            await service.handle(client_session, event)

        for j, client in enumerate(clients):
            calls = client.calls["send_event"]
            expected = [
                NostrEventUpdate(f"{j}", events[j]),
                NostrEOSE(f"{j}"),
                NostrEventUpdate(f"{j}", events[j + 10]),

            ]
            assert calls == expected
    
    @pytest.mark.asyncio
    async def test_wrong_msg(self):
        service = get_service()
        client_session = MockClientSession()
        with pytest.raises(TypeError):
            await service.handle(client_session, "hello")

    @pytest.mark.asyncio
    async def test_event_3(self, event_builder):
        service = get_service()
        client_session = MockClientSession()
        event = event_builder.create_event(
            "", kind=EventKind.ContactList, tags=
            [
                NostrTag("p", "91cf9..4e5ca", extra=["wss://alicerelay.com/", "alice"]),
                NostrTag("p", "14aeb..8dad4", extra=["wss://bobrelay.com/nostr", "bob"]),
                NostrTag("p", "612ae..e610f", extra=["ws://carolrelay.com/ws", "carol"]),
            ]
        )
        service.handle(client_session, event)
