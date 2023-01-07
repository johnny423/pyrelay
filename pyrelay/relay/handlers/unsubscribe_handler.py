from pyrelay.nostr.msgs import NostrClose
from pyrelay.relay.unit_of_work import UOW


async def unsubscribe(uow: UOW, close: NostrClose) -> None:
    async with uow:
        uow.subscriptions.unsubscribe(close.subscription_id)
