import asyncio
import logging
import random

logger = logging.getLogger(__name__)


async def run_forever(make_client):
    delay = 5
    while True:
        client = None
        try:
            client = await make_client()
            await client.run_until_disconnected()
            delay = 5
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("connection_lost")
            await asyncio.sleep(delay + random.uniform(0, 3))
            delay = min(delay * 2, 300)
        finally:
            if client:
                try:
                    await client.disconnect()
                except Exception:
                    logger.exception("disconnect_failed")
