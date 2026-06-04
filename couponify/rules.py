"""Coupon application rules.

A rule answers a single yes/no question about a cart: "is this coupon allowed to
apply?". A coupon may carry several rules; the discount engine requires *all* of
them to match (logical AND). Rules are intentionally small and concrete instead
of an arbitrary expression language, to keep the system simple and easy to test.

Rules use duck typing on the cart: any object exposing ``subtotal()`` and an
iterable ``items`` of cart lines works, which avoids importing the cart module
here and keeps the dependency graph acyclic.
"""

from __future__ import annotations

from decimal import Decimal

from .money import money


class Rule:
    """Base class for coupon eligibility rules."""

    def matches(self, cart) -> bool:  # pragma: no cover - abstract
        raise NotImplementedError


class AlwaysApplies(Rule):
    """A rule that is always satisfied."""

    def matches(self, cart) -> bool:
        return True

    def __repr__(self) -> str:
        return "AlwaysApplies()"


class MinPurchase(Rule):
    """Matches when the cart subtotal is at least ``min_value`` (inclusive)."""

    def __init__(self, min_value) -> None:
        self.min_value: Decimal = money(min_value)

    def matches(self, cart) -> bool:
        return cart.subtotal() >= self.min_value

    def __repr__(self) -> str:
        return f"MinPurchase({self.min_value})"


class HasCategory(Rule):
    """Matches when the cart contains at least one item of ``category``."""

    def __init__(self, category: str) -> None:
        self.category = category

    def matches(self, cart) -> bool:
        return any(line.item.category == self.category for line in cart.items)

    def __repr__(self) -> str:
        return f"HasCategory({self.category!r})"


class HasBrand(Rule):
    """Matches when the cart contains at least one item of ``brand``."""

    def __init__(self, brand: str) -> None:
        self.brand = brand

    def matches(self, cart) -> bool:
        return any(line.item.brand == self.brand for line in cart.items)

    def __repr__(self) -> str:
        return f"HasBrand({self.brand!r})"


class HasSeller(Rule):
    """Matches when the cart contains at least one item from ``seller``."""

    def __init__(self, seller: str) -> None:
        self.seller = seller

    def matches(self, cart) -> bool:
        return any(line.item.seller == self.seller for line in cart.items)

    def __repr__(self) -> str:
        return f"HasSeller({self.seller!r})"
