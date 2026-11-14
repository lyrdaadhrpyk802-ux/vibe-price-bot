import logging
from app.errors import ProviderError
from app.models import AssetPrice

logger = logging.getLogger(__name__)


class FallbackChain:
    def __init__(self, providers: list):
        self.providers = providers

    async def fetch(self) -> dict[str, AssetPrice]:
        errors = []
        for provider in self.providers:
            try:
                data = await provider.fetch()
                logger.info("provider_ok", extra={"provider": provider.name})
                return data
            except Exception as exc:
                logger.warning(
                    "provider_failed",
                    extra={"provider": provider.name, "error": repr(exc)},
                )
                errors.append((provider.name, exc))
        raise ProviderError(f"all providers failed: {errors}")
