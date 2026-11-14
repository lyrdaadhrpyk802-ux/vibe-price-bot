class PriceBotError(Exception):
    """Base domain error."""

class AssetNotFound(PriceBotError):
    pass

class InvalidPrice(PriceBotError):
    pass

class ProviderError(PriceBotError):
    pass
