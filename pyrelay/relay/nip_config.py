from pydantic import BaseModel

# timestamp limits relative to current time
LOWER_TIMESTAMP_OFFSET_LIMIT = - 60 * 60 * 24  # allow up to one day into the past
UPPER_TIMESTAMP_OFFSET_LIMIT = 60 * 15  # allow up to 15 minutes into the future


class NIPConfig(BaseModel):
    # NIP-9: Event deletion
    nip_9: bool = True

    # NIP-11: Relay Information Document
    nip_11: bool = False

    # NIP-12: Generic Tag Queries
    nip_12: bool = True

    # NIP-15: End of Stored Events Notice
    nip_15: bool = True

    # NIP-16: End of Stored Events Notice
    nip_16: bool = False

    # NIP-20: Command Results (implemented partly)
    nip_20: bool = True

    # NIP-22: Event created_at Limits
    nip_22: tuple = (LOWER_TIMESTAMP_OFFSET_LIMIT, UPPER_TIMESTAMP_OFFSET_LIMIT)

    # NIP-33: End of Stored Events Notice
    nip_33: bool = False

    # NIP-40: End of Stored Events Notice
    nip_40: bool = False


nips_config = NIPConfig()
