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


def test_unmatched_rule_grants_nothing():
    cart = _cart((Item(name="A", price="40", category="c", seller="s"), 1))
    coupon = Coupon(code="OFF10", discount_type=DiscountType.PERCENTAGE, value="10",
                    rules=[MinPurchase("50")])
    assert compute_discount(coupon, cart) == Decimal("0.00")


def test_empty_base_grants_nothing():
    coupon = Coupon(code="OFF10", discount_type=DiscountType.PERCENTAGE, value="10")
    assert compute_discount(coupon, Cart()) == Decimal("0.00")


def test_zero_percentage():
    cart = _cart((Item(name="A", price="100", category="c", seller="s"), 1))
    coupon = Coupon(code="ZERO", discount_type=DiscountType.PERCENTAGE, value="0")
    assert compute_discount(coupon, cart) == Decimal("0.00")


def test_full_percentage():
    cart = _cart((Item(name="A", price="100", category="c", seller="s"), 1))
    coupon = Coupon(code="ALL", discount_type=DiscountType.PERCENTAGE, value="100")
    assert compute_discount(coupon, cart) == Decimal("100.00")


def test_percentage_is_quantized():
    cart = _cart((Item(name="A", price="33.33", category="c", seller="s"), 1))
    coupon = Coupon(code="OFF10", discount_type=DiscountType.PERCENTAGE, value="10")
    # 10% of 33.33 = 3.333 -> 3.33
    assert compute_discount(coupon, cart) == Decimal("3.33")


def test_item_scope_with_no_matching_items():
    cart = _cart((Item(name="Phone", price="100", category="tech", seller="s"), 1))
    coupon = Coupon(code="BOOKS", discount_type=DiscountType.PERCENTAGE, value="20",
                    scope=CouponScope.ITEM, target_category="books")
    assert compute_discount(coupon, cart) == Decimal("0.00")


def test_max_discount_caps_percentage():
    cart = _cart((Item(name="A", price="100", category="c", seller="s"), 1))
    coupon = Coupon(code="OFF50", discount_type=DiscountType.PERCENTAGE, value="50",
                    max_discount="30")
    # 50% of 100 = 50, but capped at 30.
    assert compute_discount(coupon, cart) == Decimal("30.00")


def test_max_discount_caps_fixed():
    cart = _cart((Item(name="A", price="100", category="c", seller="s"), 1))
    coupon = Coupon(code="MINUS80", discount_type=DiscountType.FIXED, value="80",
                    max_discount="25")
    assert compute_discount(coupon, cart) == Decimal("25.00")


def test_max_discount_not_reached_keeps_amount():
    cart = _cart((Item(name="A", price="100", category="c", seller="s"), 1))
    coupon = Coupon(code="OFF10", discount_type=DiscountType.PERCENTAGE, value="10",
                    max_discount="30")
    # 10% of 100 = 10, below the 30 cap, so the full amount is granted.
    assert compute_discount(coupon, cart) == Decimal("10.00")
