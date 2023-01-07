from pyrelay.nostr.event import NostrEvent
from pyrelay.nostr.msgs import NostrCommandResults
from pyrelay.relay.client_session import ClientSession
from pyrelay.relay.relay_service import UOW


async def send_event(uow: UOW, client: ClientSession, event: NostrEvent) -> None:
    if not event.verify():  # todo: add validations + pow
        # todo: add reasons
        await client.send(
            NostrCommandResults(
                event_id=event.id,
                saved=False,
            )
        )
        return

    try:
        await uow.event_repository.add(event)  # todo: add duplicate validation
    except:
        # todo: add reasons
        await client.send(
            NostrCommandResults(
                event_id=event.id,
                saved=False,
            )
        )
    else:
        await client.send(
            NostrCommandResults(
                event_id=event.id,
                saved=True,
            )
        )
        await uow.subscriptions.broadcast(event)
