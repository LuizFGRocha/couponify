"""Discount engine.

Given a coupon and a cart, :func:`compute_discount` returns the monetary amount
the coupon grants. The engine is pure (no side effects) so it is trivial to test
in isolation, including with property-based tests.
"""

from __future__ import annotations

from decimal import Decimal

from .models import Coupon, CouponScope, DiscountType
from .money import ZERO, clamp_non_negative, money


def _discount_base(coupon: Coupon, cart) -> Decimal:
    """Return the monetary base the discount is computed over.

    For whole-cart coupons this is the cart subtotal; for item-scoped coupons it
    is the combined subtotal of the lines matching ``coupon.target_category``.
    """
    if coupon.scope is CouponScope.WHOLE_CART:
        return cart.subtotal()
    total = ZERO
    for line in cart.items:
        if line.item.category == coupon.target_category:
            total += line.subtotal
    return money(total)


def compute_discount(coupon: Coupon, cart) -> Decimal:
    """Return the discount ``coupon`` grants on ``cart``.

    Returns zero when the coupon is inactive, when any of its rules does not
    match, or when there is nothing to discount. A fixed discount never exceeds
    the base it applies to.
    """
    if not coupon.active:
        return ZERO
    if not all(rule.matches(cart) for rule in coupon.rules):
        return ZERO

    base = _discount_base(coupon, cart)
    if base <= ZERO:
        return ZERO

    if coupon.discount_type is DiscountType.PERCENTAGE:
        amount = money(base * coupon.value / Decimal(100))
    else:
        amount = money(coupon.value)
        if amount > base:
            amount = base

    return clamp_non_negative(amount)
