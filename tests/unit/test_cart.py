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


def test_total_never_negative():
    cart = Cart()
    cart.add_item(_item(price="100"), 1)
    cart.apply_coupon(Coupon(code="HUGE", discount_type=DiscountType.FIXED, value="999"))
    assert cart.total() == Decimal("0.00")


def test_total_is_subtotal_minus_discount():
    cart = Cart()
    cart.add_item(_item(price="100"), 1)
    cart.apply_coupon(Coupon(code="OFF10", discount_type=DiscountType.PERCENTAGE, value="10"))
    assert cart.total() == Decimal("90.00")


def test_apply_coupon_is_idempotent_per_code():
    cart = Cart()
    cart.add_item(_item(price="100"), 1)
    coupon = Coupon(code="OFF10", discount_type=DiscountType.PERCENTAGE, value="10")
    cart.apply_coupon(coupon)
    cart.apply_coupon(coupon)
    assert len(cart.coupons) == 1


def test_total_discount_capped_at_subtotal():
    cart = Cart()
    cart.add_item(_item(price="50"), 1)
    cart.apply_coupon(Coupon(code="A", discount_type=DiscountType.FIXED, value="40"))
    cart.apply_coupon(Coupon(code="B", discount_type=DiscountType.FIXED, value="40"))
    # Two 40.00 coupons on a 50.00 cart: discount capped at the subtotal.
    assert cart.total_discount() == Decimal("50.00")
    assert cart.total() == Decimal("0.00")


def test_is_empty():
    cart = Cart()
    assert cart.is_empty() is True
    cart.add_item(_item(), 1)
    assert cart.is_empty() is False
