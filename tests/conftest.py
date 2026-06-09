"""Shared pytest fixtures and small factories."""

from __future__ import annotations

import pytest

from couponify.cart import Cart
from couponify.models import Item
from couponify.service import CouponifyService


@pytest.fixture
def db_path(tmp_path):
    """Path to an isolated SQLite database for a single test."""
    return str(tmp_path / "couponify_test.db")


@pytest.fixture
def service(db_path):
    svc = CouponifyService(db_path)
    yield svc
    svc.close()


@pytest.fixture
def make_item():
    """Factory building items with sensible defaults."""

    def _make(name="Widget", price="10.00", category="general",
              seller="acme", margin=0.2, brand="brandx"):
        return Item(name=name, price=price, category=category, seller=seller,
                    profit_margin=margin, brand=brand)

    return _make


@pytest.fixture
def make_cart(make_item):
    """Factory building a cart from ``(item, quantity)`` pairs."""

    def _make(*lines):
        cart = Cart()
        for item, quantity in lines:
            cart.add_item(item, quantity)
        return cart

    return _make
