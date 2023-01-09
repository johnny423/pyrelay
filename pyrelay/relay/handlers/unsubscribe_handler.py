from pyrelay.nostr.msgs import NostrClose
from pyrelay.relay.unit_of_work import UnitOfWork


async def unsubscribe(uow: UnitOfWork, close: NostrClose) -> None:
    async with uow:
        uow.subscriptions.unsubscribe(close.subscription_id)
