from decimal import Decimal
from app.nlp.parser import parse_request


def test_plain_asset():
    assert parse_request("دلار").asset == "usd"
    assert parse_request("دلار").amount == Decimal("1")


def test_persian_decimal():
    req = parse_request("۲.۵ دلار")
    assert req.asset == "usd"
    assert req.amount == Decimal("2.5")


def test_english_decimal():
    req = parse_request("2.5 دلار")
    assert req.asset == "usd"
    assert req.amount == Decimal("2.5")


def test_price_prefix():
    req = parse_request("قیمت بیت‌کوین")
    assert req.asset == "btc"
    assert req.amount == Decimal("1")


def test_unknown():
    assert parse_request("hello") is None
