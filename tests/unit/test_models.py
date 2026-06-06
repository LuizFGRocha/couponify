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


def test_coupon_percentage_out_of_range():
    with pytest.raises(ValueError):
        Coupon(code="BAD", discount_type=DiscountType.PERCENTAGE, value="150")


def test_coupon_fixed_value_is_money():
    coupon = Coupon(code="MINUS5", discount_type=DiscountType.FIXED, value="5")
    assert coupon.value == Decimal("5.00")


def test_coupon_rejects_negative_fixed_value():
    with pytest.raises(ValueError):
        Coupon(code="BAD", discount_type=DiscountType.FIXED, value="-5")


def test_coupon_rejects_empty_code():
    with pytest.raises(ValueError):
        Coupon(code="", discount_type=DiscountType.FIXED, value="5")


def test_item_scope_requires_target_category():
    with pytest.raises(ValueError):
        Coupon(code="ITEM", discount_type=DiscountType.PERCENTAGE, value="10",
               scope=CouponScope.ITEM)


def test_coupon_defaults_to_always_applies():
    coupon = Coupon(code="C", discount_type=DiscountType.FIXED, value="1")
    assert len(coupon.rules) == 1
    assert isinstance(coupon.rules[0], AlwaysApplies)


def test_coupon_keeps_custom_rules():
    coupon = Coupon(code="C", discount_type=DiscountType.FIXED, value="1",
                    rules=[MinPurchase("50")])
    assert isinstance(coupon.rules[0], MinPurchase)


def test_coupon_accepts_string_enums():
    coupon = Coupon(code="C", discount_type="fixed", value="1", scope="whole_cart")
    assert coupon.discount_type is DiscountType.FIXED
    assert coupon.scope is CouponScope.WHOLE_CART
