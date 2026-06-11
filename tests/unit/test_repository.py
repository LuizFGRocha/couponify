"""Unit tests for the SQLite repositories."""

from decimal import Decimal

from couponify.database import connect, init_schema
from couponify.models import Coupon, CouponScope, DiscountType, Item
from couponify.repository import CouponRepository, ItemRepository
from couponify.rules import AlwaysApplies, MinPurchase


def _repos(db_path):
    conn = connect(db_path)
    init_schema(conn)
    return ItemRepository(conn), CouponRepository(conn)


def test_item_add_assigns_id(db_path):
    items, _ = _repos(db_path)
    stored = items.add(Item(name="A", price="10", category="c", seller="s"))
    assert stored.id is not None


def test_item_roundtrip(db_path):
    items, _ = _repos(db_path)
    stored = items.add(Item(name="Phone", price="999.90", category="tech",
                            seller="store", profit_margin=0.3, brand="acme"))
    loaded = items.get(stored.id)
    assert loaded.name == "Phone"
    assert loaded.price == Decimal("999.90")
    assert loaded.brand == "acme"


def test_item_get_by_name(db_path):
    items, _ = _repos(db_path)
    items.add(Item(name="Pen", price="2", category="office", seller="s"))
    assert items.get_by_name("Pen") is not None
    assert items.get_by_name("Missing") is None


def test_item_list_all_ordered(db_path):
    items, _ = _repos(db_path)
    items.add(Item(name="A", price="1", category="c", seller="s"))
    items.add(Item(name="B", price="2", category="c", seller="s"))
    names = [item.name for item in items.list_all()]
    assert names == ["A", "B"]


def test_item_delete(db_path):
    items, _ = _repos(db_path)
    stored = items.add(Item(name="A", price="1", category="c", seller="s"))
    assert items.delete(stored.id) is True
    assert items.get(stored.id) is None


def test_item_delete_missing_returns_false(db_path):
    items, _ = _repos(db_path)
    assert items.delete(999) is False


def test_coupon_percentage_roundtrip(db_path):
    _, coupons = _repos(db_path)
    coupons.add(Coupon(code="OFF10", discount_type=DiscountType.PERCENTAGE, value="10",
                       description="ten percent"))
    loaded = coupons.get_by_code("OFF10")
    assert loaded.discount_type is DiscountType.PERCENTAGE
    assert loaded.value == Decimal("10")
    assert loaded.description == "ten percent"


def test_coupon_fixed_roundtrip(db_path):
    _, coupons = _repos(db_path)
    coupons.add(Coupon(code="MINUS5", discount_type=DiscountType.FIXED, value="5"))
    loaded = coupons.get_by_code("MINUS5")
    assert loaded.discount_type is DiscountType.FIXED
    assert loaded.value == Decimal("5.00")


def test_coupon_min_purchase_rule_is_persisted(db_path):
    _, coupons = _repos(db_path)
    coupons.add(Coupon(code="C", discount_type=DiscountType.FIXED, value="5",
                       rules=[MinPurchase("50")]))
    loaded = coupons.get_by_code("C")
    assert isinstance(loaded.rules[0], MinPurchase)
    assert loaded.rules[0].min_value == Decimal("50.00")


def test_coupon_without_min_purchase_defaults_to_always(db_path):
    _, coupons = _repos(db_path)
    coupons.add(Coupon(code="C", discount_type=DiscountType.FIXED, value="5"))
    loaded = coupons.get_by_code("C")
    assert isinstance(loaded.rules[0], AlwaysApplies)


def test_coupon_item_scope_roundtrip(db_path):
    _, coupons = _repos(db_path)
    coupons.add(Coupon(code="BOOKS", discount_type=DiscountType.PERCENTAGE, value="20",
                       scope=CouponScope.ITEM, target_category="books"))
    loaded = coupons.get_by_code("BOOKS")
    assert loaded.scope is CouponScope.ITEM
    assert loaded.target_category == "books"


def test_coupon_set_active_toggle(db_path):
    _, coupons = _repos(db_path)
    coupons.add(Coupon(code="C", discount_type=DiscountType.FIXED, value="5"))
    assert coupons.set_active("C", False) is True
    assert coupons.get_by_code("C").active is False


def test_coupon_get_missing_returns_none(db_path):
    _, coupons = _repos(db_path)
    assert coupons.get_by_code("NOPE") is None


def test_coupon_delete(db_path):
    _, coupons = _repos(db_path)
    coupons.add(Coupon(code="C", discount_type=DiscountType.FIXED, value="5"))
    assert coupons.delete("C") is True
    assert coupons.get_by_code("C") is None
