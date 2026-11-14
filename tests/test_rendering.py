from app.rendering.card import make_price_card


def test_card_is_png():
    buf = make_price_card(
        title="USD",
        price_text="258465",
        unit="IRT",
        change_pct=1.2,
        values=[250000, 252000, 255000, 258465],
        age_text="5 min ago",
        source="usd",
        is_stale=False,
    )
    assert buf.getvalue()[:8] == b"\x89PNG\r\n\x1a\n"
