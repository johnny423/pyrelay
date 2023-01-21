import time

from pyrelay.nostr.event import EventKind, NostrEvent
from pyrelay.nostr.msgs import NostrCommandResults
from pyrelay.relay.client_session import ClientSession
from pyrelay.relay.nip_config import nips_config
from pyrelay.relay.relay_service import EventsRepository
from pyrelay.relay.unit_of_work import UnitOfWork


async def send_event(uow: UnitOfWork, client: ClientSession, event: NostrEvent) -> None:
    """
    NIP-01
    NIP-09 event deletion todo: test + support reference events
    NIP-20 command results
    """
    async with uow:
        msg = await _save_event(uow.events, event)

        if nips_config.nip_20:
            await client.send(msg)

        if msg.saved:
            await uow.subscriptions.broadcast(event)


async def _save_event(repo: EventsRepository, event: NostrEvent) -> NostrCommandResults:
    if not event.verify():
        return NostrCommandResults(
            event_id=event.id, saved=False, message="invalid: signature is wrong"
        )

    if nips_config.nip_9 and event.kind == EventKind.EventDeletion:  # type: ignore
        await _handle_delete_event(repo, event)

    if not is_creation_time_valid(event.created_at, time.time(), nips_config.nip_22):
        return NostrCommandResults(
            event_id=event.id, saved=False, message="invalid: timestamp is not in required time frame"
        )

    try:
        # todo: add duplicate validation
        await repo.add(event)
    except Exception:
        return NostrCommandResults(
            event_id=event.id, saved=False, message="error: failed to add event"
        )
    else:
        return NostrCommandResults(event_id=event.id, saved=True)


async def _handle_delete_event(repo: EventsRepository, event: NostrEvent):
    keys_to_delete = event.e_tags
    await repo.delete(keys_to_delete)


def is_creation_time_valid(event_creation_time: int, current_time: float, nip_22_config: tuple[int, int]) -> bool:
    if not nip_22_config:
        return True
    creation_time_offset = event_creation_time - current_time
    return int(creation_time_offset) in range(*nip_22_config)
