"""Unit tests for the discount engine."""

from decimal import Decimal

from couponify.cart import Cart
from couponify.discounts import compute_discount
from couponify.models import Coupon, CouponScope, DiscountType, Item
from couponify.rules import MinPurchase


def _cart(*lines):
    cart = Cart()
    for item, qty in lines:
        cart.add_item(item, qty)
    return cart


def test_percentage_on_whole_cart():
    cart = _cart((Item(name="A", price="100", category="c", seller="s"), 1))
    coupon = Coupon(code="OFF10", discount_type=DiscountType.PERCENTAGE, value="10")
    assert compute_discount(coupon, cart) == Decimal("10.00")


def test_fixed_on_whole_cart():
    cart = _cart((Item(name="A", price="100", category="c", seller="s"), 1))
    coupon = Coupon(code="MINUS15", discount_type=DiscountType.FIXED, value="15")
    assert compute_discount(coupon, cart) == Decimal("15.00")


def test_fixed_never_exceeds_base():
    cart = _cart((Item(name="A", price="100", category="c", seller="s"), 1))
    coupon = Coupon(code="HUGE", discount_type=DiscountType.FIXED, value="200")
    assert compute_discount(coupon, cart) == Decimal("100.00")


def test_item_scope_targets_only_matching_category():
    cart = _cart(
        (Item(name="Book", price="50", category="books", seller="s"), 1),
        (Item(name="Phone", price="100", category="tech", seller="s"), 1),
    )
    coupon = Coupon(code="BOOKS20", discount_type=DiscountType.PERCENTAGE, value="20",
                    scope=CouponScope.ITEM, target_category="books")
    # 20% of the 50.00 worth of books only.
    assert compute_discount(coupon, cart) == Decimal("10.00")


def test_inactive_coupon_grants_nothing():
    cart = _cart((Item(name="A", price="100", category="c", seller="s"), 1))
    coupon = Coupon(code="OFF10", discount_type=DiscountType.PERCENTAGE, value="10",
                    active=False)
    assert compute_discount(coupon, cart) == Decimal("0.00")
