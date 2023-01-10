from typing import Collection

from pyrelay.nostr.event import NostrEvent
from pyrelay.nostr.msgs import NostrEOSE, NostrEventUpdate, NostrRequest
from pyrelay.relay.client_session import ClientSession
from pyrelay.relay.nip_config import nips_config
from pyrelay.relay.unit_of_work import UnitOfWork


async def subscribe(
    uow: UnitOfWork, client: ClientSession, request: NostrRequest
) -> None:
    async with uow:
        events = await uow.events.query(*request.filters)
        await _send_stored_events(client, request.subscription_id, events)

        uow.subscriptions.subscribe(request, client)


async def _send_stored_events(
    client: ClientSession,
    subscription_id: str,
    events: Collection[NostrEvent],
) -> None:
    if not events:
        return

    for event in events:
        event_update = NostrEventUpdate(subscription_id=subscription_id, event=event)
        await client.send(event_update)

    if nips_config.nip_15:
        endmsg = NostrEOSE(subscription_id)
        await client.send(endmsg)
