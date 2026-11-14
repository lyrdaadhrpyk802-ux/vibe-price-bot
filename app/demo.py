"""Local demo without any messaging framework."""
import asyncio
from pathlib import Path

from app.bot import PriceBot
from app.config import settings
from app.logging_config import setup_logging
from app.main import build_service


async def main() -> None:
    setup_logging(settings.log_level)
    service = await build_service()
    bot = PriceBot(service)

    print("Fetching data from Iran Market and CoinGecko...")
    try:
        await service._iran_all()
        await service._crypto_all()
        print("Cache populated")
    except Exception as exc:
        print(f"Fetch error: {exc}")

    out_dir = Path("demo-output")
    out_dir.mkdir(exist_ok=True)

    samples = ["dollar", "2.5 dollar", "bitcoin", "gold", "hello", "/help"]
    for sample in samples:
        text, photo = await bot.handle_text(sample)
        safe = sample.replace(" ", "-").replace("/", "").replace(".", "_")
        if photo:
            path = out_dir / f"card-{safe}.png"
            path.write_bytes(photo.getvalue())
            print(f"-> {sample!r}: [IMAGE] {path} ({len(photo.getvalue())} bytes)")
        else:
            first_line = (text or "").split("\n", 1)[0]
            print(f"-> {sample!r}: [TEXT] {first_line[:70]!r}")

    print(f"\nCards saved to {out_dir}/")


if __name__ == "__main__":
    asyncio.run(main())
