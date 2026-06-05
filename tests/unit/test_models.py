"""Unit tests for the domain models."""

from decimal import Decimal

import pytest

from couponify.models import (
    CartItem,
    Coupon,
    CouponScope,
    DiscountType,
    Item,
)
from couponify.rules import AlwaysApplies, MinPurchase


def test_item_converts_price_to_money():
    item = Item(name="Phone", price="999.9", category="tech", seller="store")
    assert item.price == Decimal("999.90")


def test_item_rejects_negative_price():
    with pytest.raises(ValueError):
        Item(name="Phone", price="-1", category="tech", seller="store")


def test_item_rejects_empty_name():
    with pytest.raises(ValueError):
        Item(name="   ", price="10", category="tech", seller="store")


def test_item_rejects_margin_above_one():
    with pytest.raises(ValueError):
        Item(name="Phone", price="10", category="tech", seller="store", profit_margin=1.5)


@pytest.mark.parametrize("margin", [0.0, 0.5, 1.0])
def test_item_accepts_margin_in_range(margin):
    item = Item(name="Phone", price="10", category="tech", seller="store",
                profit_margin=margin)
    assert item.profit_margin == margin


def test_cart_item_subtotal():
    item = Item(name="Pen", price="2.50", category="office", seller="store")
    assert CartItem(item=item, quantity=3).subtotal == Decimal("7.50")


def test_cart_item_rejects_zero_quantity():
    item = Item(name="Pen", price="2.50", category="office", seller="store")
    with pytest.raises(ValueError):
        CartItem(item=item, quantity=0)


def test_coupon_percentage_keeps_numeric_value():
    coupon = Coupon(code="OFF10", discount_type=DiscountType.PERCENTAGE, value="10")
    assert coupon.value == Decimal("10")
    assert coupon.discount_type is DiscountType.PERCENTAGE
