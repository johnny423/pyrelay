import time
import uuid
from collections import defaultdict

import pytest

from pyrelay.nostr.event import EventKind, NostrTag, NostrDataType
from pyrelay.nostr.event_builder import EventBuilder
from pyrelay.nostr.filters import NostrFilter
from pyrelay.nostr.msgs import NostrEventUpdate, NostrRequest, NostrClose, NostrEOSE
from pyrelay.relay.bootstrap import get_uow_factory
from pyrelay.relay.client_session import BaseClientSession
from pyrelay.relay.dispatcher import RelayDispatcher
from pyrelay.relay.nip_config import nips_config


@pytest.fixture(scope="module")
def event_builder():
    return EventBuilder.from_generated()


class MockClientSession(BaseClientSession):
    def __init__(self):
        super(MockClientSession, self).__init__()
        self.calls = defaultdict(list)
        self.uid = uuid.uuid4()

    async def send(self, event_update: NostrDataType):
        self.calls["send_event"].append(event_update)


def get_dispatcher():
    uow_factory = get_uow_factory(in_memory=True)
    dispatcher = RelayDispatcher(uow_factory)
    return dispatcher


async def _attempt_timestamp(event_builder, timestamps: list[int], should_save: bool):
    dispatcher = get_dispatcher()
    client_session = MockClientSession()
    for timestamp in timestamps:
        event = event_builder.create_event(
            "", created_at=timestamp
        )
        await dispatcher.handle(client_session, event)
    for msg in list(client_session.calls.values())[0]:  # todo make prettier access to values
        assert msg.saved == should_save


class TestRelayDispatcher:
    @pytest.mark.asyncio
    async def test_report_and_save_events(self, event_builder):
        dispatcher = get_dispatcher()

        events = []
        for i in range(10):
            event = event_builder.create_event(f"{i}")
            events.append(event)
            client_session = MockClientSession()
            await dispatcher.handle(client_session, event)

        async with dispatcher.uow_factory() as uow:
            result = await uow.events.query()

        assert events == result

    @pytest.mark.asyncio
    async def test_subscribe_and_broadcast(self):
        dispatcher = get_dispatcher()

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
            await dispatcher.handle(client_session, event)

        # Subscribe to events and query
        clients = []
        for j, event_builder in enumerate(event_builders):
            subscribe_request = NostrRequest(
                subscription_id=f"{j}",
                filters=[NostrFilter(authors=[event_builder.pub_key])]
            )
            subscriber_client_session = MockClientSession()
            await dispatcher.handle(subscriber_client_session, subscribe_request)
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
            await dispatcher.handle(client_session, event)

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
            await dispatcher.handle(client, NostrClose(f"{j}"))

        for i, event_builder in enumerate(event_builders):
            event = event_builder.create_event(f"{i * 3}")
            events.append(event)
            client_session = MockClientSession()
            await dispatcher.handle(client_session, event)

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
        dispatcher = get_dispatcher()
        client_session = MockClientSession()
        with pytest.raises(TypeError):
            await dispatcher.handle(client_session, "hello")

    @pytest.mark.asyncio
    async def test_event_3(self, event_builder):
        dispatcher = get_dispatcher()
        client_session = MockClientSession()
        event = event_builder.create_event(
            "", kind=EventKind.ContactList, tags=
            [
                NostrTag("p", "91cf9..4e5ca", extra=["wss://alicerelay.com/", "alice"]),
                NostrTag("p", "14aeb..8dad4", extra=["wss://bobrelay.com/nostr", "bob"]),
                NostrTag("p", "612ae..e610f", extra=["ws://carolrelay.com/ws", "carol"]),
            ]
        )
        await dispatcher.handle(client_session, event)

    @pytest.mark.asyncio
    async def test_legal_timestamp(self, event_builder):
        nip_22_config = nips_config.nip_22
        if not nip_22_config:
            return
        current_time = time.time()
        legal_timeframe_size = nip_22_config[1] - nip_22_config[0]
        lower_bound_timestamp = current_time + nip_22_config[0]
        amount = 5
        # do not check lower bound as it can fail due to runtime delay
        legal_timestamps = [lower_bound_timestamp + legal_timeframe_size / amount * i for i in range(1, amount + 1)]
        await _attempt_timestamp(event_builder=event_builder, timestamps=legal_timestamps, should_save=True)

    @pytest.mark.asyncio
    async def test_illegal_timestamp(self, event_builder):
        nip_22_config = nips_config.nip_22
        if not nip_22_config:
            return
        current_time = time.time()
        illegal_timestamps = [
            int(current_time + nip_22_config[0] - 60),  # a minute before lower limit
            int(current_time + nip_22_config[1] + 60)  # a minute after upper limit
        ]
        await _attempt_timestamp(event_builder=event_builder, timestamps=illegal_timestamps, should_save=False)
