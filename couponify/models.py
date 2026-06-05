"""Domain models: items and coupons.

The system simulates a marketplace shopping cart. An :class:`Item` is a product
with a price and a few descriptive properties. A :class:`Coupon` carries a
discount (percentage or fixed) and the rules that decide when it applies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from .money import money

# Rules are imported lazily inside the dataclass default to avoid any risk of
# circular imports; ``rules`` only depends on ``money`` so this is safe.
from .rules import Rule, AlwaysApplies


class DiscountType(str, Enum):
    """How the discount value should be interpreted."""

    PERCENTAGE = "percentage"
    FIXED = "fixed"


class CouponScope(str, Enum):
    """What the discount is computed over."""

    WHOLE_CART = "whole_cart"
    ITEM = "item"


@dataclass
class Item:
    """A product that can be added to the cart."""

    name: str
    price: Decimal
    category: str
    seller: str
    profit_margin: float = 0.0
    brand: str = ""
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("item name must not be empty")
        self.price = money(self.price)
        if self.price < money(0):
            raise ValueError("item price must not be negative")
        if not 0.0 <= float(self.profit_margin) <= 1.0:
            raise ValueError("profit_margin must be between 0 and 1")


@dataclass
class CartItem:
    """An :class:`Item` together with a quantity inside the cart."""

    item: Item
    quantity: int = 1

    def __post_init__(self) -> None:
        if self.quantity < 1:
            raise ValueError("quantity must be at least 1")

    @property
    def subtotal(self) -> Decimal:
        """Price of this line: unit price times quantity."""
        return money(self.item.price * self.quantity)


@dataclass
class Coupon:
    """A discount with the rules that gate its application.

    ``value`` means a percentage (0-100) when ``discount_type`` is
    ``PERCENTAGE`` and a monetary amount when it is ``FIXED``. When ``scope`` is
    ``ITEM`` the discount is computed only over the cart lines whose category
    matches ``target_category``. ``max_discount`` is an optional cap on the
    amount granted (enforced by the discount engine).
    """

    code: str
    discount_type: DiscountType
    value: Decimal
    description: str = ""
    scope: CouponScope = CouponScope.WHOLE_CART
    target_category: Optional[str] = None
    rules: List[Rule] = field(default_factory=lambda: [AlwaysApplies()])
    active: bool = True
    max_discount: Optional[Decimal] = None

    def __post_init__(self) -> None:
        if not self.code or not self.code.strip():
            raise ValueError("coupon code must not be empty")
        self.discount_type = DiscountType(self.discount_type)
        self.scope = CouponScope(self.scope)
        if self.discount_type is DiscountType.PERCENTAGE:
            self.value = Decimal(str(self.value))
            if not Decimal("0") <= self.value <= Decimal("100"):
                raise ValueError("percentage value must be between 0 and 100")
        else:
            self.value = money(self.value)
            if self.value < money(0):
                raise ValueError("fixed discount must not be negative")
        if self.scope is CouponScope.ITEM and not self.target_category:
            raise ValueError("item-scoped coupon requires a target_category")
        if self.max_discount is not None:
            self.max_discount = money(self.max_discount)
        if not self.rules:
            self.rules = [AlwaysApplies()]
