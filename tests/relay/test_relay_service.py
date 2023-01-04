from collections import defaultdict

import pytest

from pynostr.nostr.event_builder import EventBuilder
from pynostr.nostr.filters import NostrFilter
from pynostr.nostr.requests import NostrEventUpdate, NostrRequest, NostrClose
from pynostr.relay.client_session import BaseClientSession
from pynostr.relay.relay_service import RelayService, Subscriptions
from pynostr.relay.repos.in_memory_event_repo import InMemoryEventsRepository


@pytest.fixture(scope="module")
def event_builder():
    return EventBuilder.from_generated()


class MockClientSession(BaseClientSession):
    def __init__(self):
        super(MockClientSession, self).__init__()
        self.calls = defaultdict(list)

    async def send_event(self, event_update: NostrEventUpdate):
        self.calls["send_event"].append(event_update)


def get_service():
    repo = InMemoryEventsRepository()
    subs = Subscriptions()
    service = RelayService(repo, subs)
    return service


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

        result = await service.event_repository.query()
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
            assert [event_update.event for event_update in calls] == [events[j]]

        # Report events and broadcast to subscribers
        for i, event_builder in enumerate(event_builders):
            event = event_builder.create_event(f"{i*2}")
            events.append(event)
            client_session = MockClientSession()
            await service.handle(client_session, event)

        for j, client in enumerate(clients):
            calls = client.calls["send_event"]
            assert [event_update.event for event_update in calls] == [events[j], events[j + 10]]

        # Un-subscribe
        for j, client in enumerate(clients):
            await service.handle(client, NostrClose(f"{j}"))

        for i, event_builder in enumerate(event_builders):
            event = event_builder.create_event(f"{i*3}")
            events.append(event)
            client_session = MockClientSession()
            await service.handle(client_session, event)

        for j, client in enumerate(clients):
            calls = client.calls["send_event"]
            assert [event_update.event for event_update in calls] == [events[j], events[j + 10]]

    @pytest.mark.asyncio
    async def test_wrong_msg(self):
        service = get_service()
        client_session = MockClientSession()
        with pytest.raises(TypeError):
            await service.handle(client_session, "hello")
