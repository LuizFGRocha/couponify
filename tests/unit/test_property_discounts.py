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
