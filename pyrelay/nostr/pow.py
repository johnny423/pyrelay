from binascii import unhexlify

from pyrelay.nostr.event import EventId, NostrEvent


def difficulty(event_id: EventId) -> int:
    """
    Compute the difficulty of an event id based on NIP-13
    https://github.com/nostr-protocol/nips/blob/master/13.md

    From the post
    | Difficulty is defined to be the number of leading zero bits in the NIP-01 id.
    | For example, an id of "000000000e9d97a1ab09fc381030b346cdd7a142ad57e6df0b46dc9bef6c7e2d"
    | has a difficulty of 36 with 36 leading 0 bits.
    """
    digest = unhexlify(event_id)
    return 256 - int.from_bytes(digest, "big").bit_length()


def validate_pow(event: NostrEvent) -> bool:
    if not event.verify():
        return False

    nonce_tags = (tag for tag in event.tags if tag.type == "nonce")
    nonce_tag = next(nonce_tags, None)
    if not nonce_tag:
        # no pow should have done
        return True

    try:
        # Expected structure ["nonce", "1", "20"]
        [_, _, target] = nonce_tag
        target_difficulty = int(target)
    except ValueError:
        # Bad tag structure
        return False

    return difficulty(event.id) >= target_difficulty
