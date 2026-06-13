"""Couponify: marketplace shopping cart simulator with dynamic discounts."""

from .cart import Cart
from .discounts import compute_discount
from .models import CartItem, Coupon, CouponScope, DiscountType, Item
from .money import money
from .rules import (
    AlwaysApplies,
    HasBrand,
    HasCategory,
    HasSeller,
    MinPurchase,
    Rule,
)

__version__ = "0.1.0"

__all__ = [
    "Cart",
    "CartItem",
    "Coupon",
    "CouponScope",
    "DiscountType",
    "Item",
    "Rule",
    "AlwaysApplies",
    "MinPurchase",
    "HasCategory",
    "HasBrand",
    "HasSeller",
    "compute_discount",
    "money",
    "__version__",
]
