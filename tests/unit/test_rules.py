"""Unit tests for coupon eligibility rules."""

from couponify.cart import Cart
from couponify.models import Item
from couponify.rules import (
    AlwaysApplies,
    HasBrand,
    HasCategory,
    HasSeller,
    MinPurchase,
)


def _cart(*items):
    cart = Cart()
    for item in items:
        cart.add_item(item)
    return cart


def test_always_applies_is_true():
    assert AlwaysApplies().matches(_cart()) is True


def test_min_purchase_below_threshold():
    cart = _cart(Item(name="A", price="40", category="c", seller="s"))
    assert MinPurchase("50").matches(cart) is False


def test_min_purchase_at_threshold_is_inclusive():
    cart = _cart(Item(name="A", price="50", category="c", seller="s"))
    assert MinPurchase("50").matches(cart) is True


def test_min_purchase_above_threshold():
    cart = _cart(Item(name="A", price="60", category="c", seller="s"))
    assert MinPurchase("50").matches(cart) is True


def test_has_category_present():
    cart = _cart(Item(name="A", price="10", category="books", seller="s"))
    assert HasCategory("books").matches(cart) is True


def test_has_category_absent():
    cart = _cart(Item(name="A", price="10", category="books", seller="s"))
    assert HasCategory("tech").matches(cart) is False


def test_has_brand_present():
    cart = _cart(Item(name="A", price="10", category="c", seller="s", brand="nike"))
    assert HasBrand("nike").matches(cart) is True


def test_has_brand_absent():
    cart = _cart(Item(name="A", price="10", category="c", seller="s", brand="nike"))
    assert HasBrand("adidas").matches(cart) is False


def test_has_seller_present():
    cart = _cart(Item(name="A", price="10", category="c", seller="acme"))
    assert HasSeller("acme").matches(cart) is True


def test_has_seller_absent():
    cart = _cart(Item(name="A", price="10", category="c", seller="acme"))
    assert HasSeller("other").matches(cart) is False


def test_min_purchase_repr_is_readable():
    assert repr(MinPurchase("10")) == "MinPurchase(10.00)"
    
    
def test_has_brand_repr_is_readable():
    assert repr(HasBrand("nike")) == "HasBrand('nike')"
    
    
def test_has_seller_repr_is_readable():
    assert repr(HasSeller("acme")) == "HasSeller('acme')"
    
    
def test_has_category_repr_is_readable():
    assert repr(HasCategory("books")) == "HasCategory('books')"
    
    
def test_always_applies_repr_is_readable():
    assert repr(AlwaysApplies()) == "AlwaysApplies()"
