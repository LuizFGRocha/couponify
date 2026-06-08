"""Unit tests for the cart aggregate."""

from decimal import Decimal

from couponify.cart import Cart
from couponify.models import Coupon, DiscountType, Item


def _item(name="A", price="10", category="c", seller="s", item_id=None):
    item = Item(name=name, price=price, category=category, seller=seller)
    item.id = item_id
    return item


def test_empty_cart_subtotal_is_zero():
    assert Cart().subtotal() == Decimal("0.00")


def test_subtotal_sums_lines():
    cart = Cart()
    cart.add_item(_item(price="10"), 2)
    cart.add_item(_item(name="B", price="5"), 1)
    assert cart.subtotal() == Decimal("25.00")


def test_add_item_merges_same_item_by_id():
    cart = Cart()
    item = _item(price="10", item_id=1)
    cart.add_item(item, 1)
    cart.add_item(item, 2)
    assert len(cart.items) == 1
    assert cart.items[0].quantity == 3


def test_total_discount_sums_coupons():
    cart = Cart()
    cart.add_item(_item(price="100"), 1)
    cart.apply_coupon(Coupon(code="A", discount_type=DiscountType.FIXED, value="10"))
    cart.apply_coupon(Coupon(code="B", discount_type=DiscountType.PERCENTAGE, value="10"))
    assert cart.total_discount() == Decimal("20.00")

