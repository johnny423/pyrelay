from pyrelay.nostr.msgs import NostrClose
from pyrelay.relay.relay_service import UOW


async def unsubscribe(uow: UOW, close: NostrClose) -> None:
    uow.subscriptions.unsubscribe(close.subscription_id)
