"""Application service.

``CouponifyService`` is the façade used by the CLI. It owns the database
connection, exposes item/coupon registration and manages a single shared cart
persisted across invocations.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from .cart import Cart
from .database import connect, init_schema
from .models import Coupon, Item
from .repository import CouponRepository, ItemRepository


class CouponifyService:
    """High level operations over the marketplace cart."""

    def __init__(self, db_path: str) -> None:
        self.conn = connect(db_path)
        init_schema(self.conn)
        self.items = ItemRepository(self.conn)
        self.coupons = CouponRepository(self.conn)

    # -- items ---------------------------------------------------------------

    def add_item(self, name: str, price, category: str, seller: str,
                 profit_margin: float = 0.0, brand: str = "") -> Item:
        item = Item(name=name, price=price, category=category, seller=seller,
                    profit_margin=profit_margin, brand=brand)
        return self.items.add(item)

    def list_items(self) -> List[Item]:
        return self.items.list_all()

    def get_item(self, item_id: int) -> Optional[Item]:
        return self.items.get(item_id)

    # -- coupons -------------------------------------------------------------

    def add_coupon(self, coupon: Coupon) -> Coupon:
        return self.coupons.add(coupon)

    def list_coupons(self) -> List[Coupon]:
        return self.coupons.list_all()

    def set_coupon_active(self, code: str, active: bool) -> bool:
        return self.coupons.set_active(code, active)

    # -- cart ----------------------------------------------------------------

    def add_to_cart(self, item_id: int, quantity: int = 1) -> Item:
        item = self.items.get(item_id)
        if item is None:
            raise LookupError(f"item {item_id} not found")
        if quantity < 1:
            raise ValueError("quantity must be at least 1")
        self.conn.execute(
            "INSERT INTO cart_items (item_id, quantity) VALUES (?, ?)",
            (item_id, quantity),
        )
        self.conn.commit()
        return item

    def apply_coupon_to_cart(self, code: str) -> bool:
        if self.coupons.get_by_code(code) is None:
            return False
        self.conn.execute(
            "INSERT OR IGNORE INTO cart_coupons (coupon_code) VALUES (?)", (code,)
        )
        self.conn.commit()
        return True

    def clear_cart(self) -> None:
        self.conn.execute("DELETE FROM cart_items")
        self.conn.execute("DELETE FROM cart_coupons")
        self.conn.commit()

    def cart_lines(self) -> List[Tuple[Item, int]]:
        cart = self.build_cart()
        return [(line.item, line.quantity) for line in cart.items]

    def build_cart(self) -> Cart:
        """Reconstruct the persisted cart as a domain :class:`Cart`."""
        cart = Cart()
        rows = self.conn.execute(
            "SELECT item_id, quantity FROM cart_items ORDER BY id"
        ).fetchall()
        for row in rows:
            item = self.items.get(row["item_id"])
            if item is not None:
                cart.add_item(item, row["quantity"])
        codes = self.conn.execute(
            "SELECT coupon_code FROM cart_coupons ORDER BY id"
        ).fetchall()
        for code_row in codes:
            coupon = self.coupons.get_by_code(code_row["coupon_code"])
            if coupon is not None:
                cart.apply_coupon(coupon)
        return cart

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "CouponifyService":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
