"""The shopping cart aggregate.

A :class:`Cart` holds cart lines and the coupons applied to it, and knows how to
compute its subtotal, total discount and final total. The total can never be
negative, no matter how aggressive the applied coupons are.
"""

from __future__ import annotations

from decimal import Decimal
from typing import List

from .discounts import compute_discount
from .models import CartItem, Coupon, Item
from .money import ZERO, clamp_non_negative, money


class Cart:
    """An in-memory shopping cart."""

    def __init__(self) -> None:
        self.items: List[CartItem] = []
        self.coupons: List[Coupon] = []

    def add_item(self, item: Item, quantity: int = 1) -> CartItem:
        """Add ``quantity`` units of ``item``.

        If the item is already in the cart the quantities are merged into the
        existing line instead of creating a duplicate.
        """
        for line in self.items:
            if line.item.id is not None and line.item.id == item.id:
                line.quantity += quantity
                return line
            if line.item.id is None and line.item is item:
                line.quantity += quantity
                return line
        line = CartItem(item=item, quantity=quantity)
        self.items.append(line)
        return line

    def apply_coupon(self, coupon: Coupon) -> None:
        """Attach a coupon to the cart (idempotent per coupon code)."""
        if any(c.code == coupon.code for c in self.coupons):
            return
        self.coupons.append(coupon)

    def subtotal(self) -> Decimal:
        """Sum of every cart line, before any discount."""
        total = ZERO
        for line in self.items:
            total += line.subtotal
        return money(total)

    def total_discount(self) -> Decimal:
        """Combined discount granted by all applied coupons, capped at subtotal."""
        total = ZERO
        for coupon in self.coupons:
            total += compute_discount(coupon, self)
        return money(min(total, self.subtotal()))

    def total(self) -> Decimal:
        """Final amount due: subtotal minus discount, never below zero."""
        return clamp_non_negative(money(self.subtotal() - self.total_discount()))

    def is_empty(self) -> bool:
        return not self.items
