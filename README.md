# Vibe Price Bot

Crypto / fiat / gold price bot. Pure Python, framework-agnostic adapter.

## Setup

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env

## Run

    python -m app.demo      # local test, no framework
    pytest -q               # tests

## Layout

- app/nlp/        - Persian/Arabic digit normalization + parser
- app/providers/  - Iran Market, CoinGecko, FallbackChain
- app/cache.py    - TTL cache with stale fallback
- app/service.py  - price service
- app/rendering/  - Pillow card generator
- app/bot.py      - framework-independent logic
- app/adapter.py  - bridge to any framework (send_text + send_photo)
