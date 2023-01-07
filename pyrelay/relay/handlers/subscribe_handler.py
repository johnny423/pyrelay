from typing import Collection

from pyrelay.nostr.event import NostrEvent
from pyrelay.nostr.msgs import NostrEOSE, NostrEventUpdate, NostrRequest
from pyrelay.relay.client_session import ClientSession
from pyrelay.relay.relay_service import UOW


async def subscribe(uow: UOW, client: ClientSession, request: NostrRequest) -> None:
    events = await uow.event_repository.query(*request.filters)
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

    endmsg = NostrEOSE(subscription_id)
    await client.send(endmsg)