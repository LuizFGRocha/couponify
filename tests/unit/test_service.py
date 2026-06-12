"""Unit tests for the application service."""

from decimal import Decimal

import pytest

from couponify.models import Coupon, DiscountType


def test_add_and_list_items(service):
    service.add_item(name="Phone", price="100", category="tech", seller="store")
    items = service.list_items()
    assert len(items) == 1
    assert items[0].name == "Phone"


def test_add_and_list_coupons(service):
    service.add_coupon(Coupon(code="OFF10", discount_type=DiscountType.PERCENTAGE, value="10"))
    coupons = service.list_coupons()
    assert [c.code for c in coupons] == ["OFF10"]


def test_add_to_cart_and_build(service):
    item = service.add_item(name="Phone", price="100", category="tech", seller="store")
    service.add_to_cart(item.id, 2)
    cart = service.build_cart()
    assert cart.subtotal() == Decimal("200.00")


def test_add_to_cart_unknown_item_raises(service):
    with pytest.raises(LookupError):
        service.add_to_cart(999, 1)


def test_apply_coupon_to_cart_returns_false_when_missing(service):
    assert service.apply_coupon_to_cart("NOPE") is False


def test_checkout_applies_discount(service):
    item = service.add_item(name="Phone", price="100", category="tech", seller="store")
    service.add_to_cart(item.id, 1)
    service.add_coupon(Coupon(code="OFF10", discount_type=DiscountType.PERCENTAGE, value="10"))
    assert service.apply_coupon_to_cart("OFF10") is True
    cart = service.build_cart()
    assert cart.total() == Decimal("90.00")


def test_clear_cart(service):
    item = service.add_item(name="Phone", price="100", category="tech", seller="store")
    service.add_to_cart(item.id, 1)
    service.clear_cart()
    assert service.build_cart().is_empty() is True


def test_cart_lines_helper(service):
    item = service.add_item(name="Phone", price="100", category="tech", seller="store")
    service.add_to_cart(item.id, 3)
    lines = service.cart_lines()
    assert lines[0][0].name == "Phone"
    assert lines[0][1] == 3
