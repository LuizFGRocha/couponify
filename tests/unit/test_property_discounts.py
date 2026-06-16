"""Property-based tests (Hypothesis) for the discount engine invariants."""

from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st

from couponify.cart import Cart
from couponify.discounts import compute_discount
from couponify.models import Coupon, DiscountType, Item
from couponify.money import ZERO, clamp_non_negative, money

# Prices as an exact amount of cents turned into money (0.00 .. 10000.00).
prices = st.integers(min_value=0, max_value=1_000_000).map(lambda c: money(Decimal(c) / 100))
quantities = st.integers(min_value=1, max_value=20)
percentages = st.integers(min_value=0, max_value=100)


def _single_item_cart(price, quantity):
    cart = Cart()
    cart.add_item(Item(name="X", price=price, category="c", seller="s"), quantity)
    return cart


@given(price=prices, quantity=quantities, pct=percentages)
def test_percentage_discount_within_base(price, quantity, pct):
    cart = _single_item_cart(price, quantity)
    coupon = Coupon(code="P", discount_type=DiscountType.PERCENTAGE, value=pct)
    discount = compute_discount(coupon, cart)
    assert ZERO <= discount <= cart.subtotal()


@given(price=prices, quantity=quantities, value=prices)
def test_fixed_discount_within_base(price, quantity, value):
    cart = _single_item_cart(price, quantity)
    coupon = Coupon(code="F", discount_type=DiscountType.FIXED, value=value)
    discount = compute_discount(coupon, cart)
    assert ZERO <= discount <= cart.subtotal()


@given(price=prices, quantity=quantities, pct=percentages)
def test_total_between_zero_and_subtotal(price, quantity, pct):
    cart = _single_item_cart(price, quantity)
    cart.apply_coupon(Coupon(code="P", discount_type=DiscountType.PERCENTAGE, value=pct))
    assert ZERO <= cart.total() <= cart.subtotal()
    expected = clamp_non_negative(cart.subtotal() - cart.total_discount())
    assert cart.total() == expected


@given(st.integers(min_value=-10**9, max_value=10**9))
def test_money_quantization_is_idempotent(n):
    value = Decimal(n) / 100
    assert money(money(value)) == money(value)
