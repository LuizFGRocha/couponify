"""Unit tests for coupon eligibility rules."""

from couponify.cart import Cart
from couponify.models import Item
from couponify.rules import (
    AlwaysApplies,
    HasBrand,
    HasCategory,
    HasSeller,
    MinPurchase,
)


def _cart(*items):
    cart = Cart()
    for item in items:
        cart.add_item(item)
    return cart


def test_always_applies_is_true():
    assert AlwaysApplies().matches(_cart()) is True


def test_min_purchase_below_threshold():
    cart = _cart(Item(name="A", price="40", category="c", seller="s"))
    assert MinPurchase("50").matches(cart) is False


def test_min_purchase_at_threshold_is_inclusive():
    cart = _cart(Item(name="A", price="50", category="c", seller="s"))
    assert MinPurchase("50").matches(cart) is True


def test_min_purchase_above_threshold():
    cart = _cart(Item(name="A", price="60", category="c", seller="s"))
    assert MinPurchase("50").matches(cart) is True

