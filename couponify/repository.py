"""Repositories: translate between domain objects and SQLite rows.

To keep persistence simple, a stored coupon only remembers its most common
eligibility rule (a minimum purchase). The richer in-memory rule set lives in
the domain layer and is exercised by the unit tests.
"""

from __future__ import annotations

import sqlite3
from typing import List, Optional

from .models import Coupon, CouponScope, DiscountType, Item
from .rules import AlwaysApplies, MinPurchase


class ItemRepository:
    """CRUD access to the ``items`` table."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add(self, item: Item) -> Item:
        cur = self.conn.execute(
            "INSERT INTO items (name, price, category, seller, profit_margin, brand) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (item.name, str(item.price), item.category, item.seller,
             float(item.profit_margin), item.brand),
        )
        self.conn.commit()
        item.id = cur.lastrowid
        return item

    def get(self, item_id: int) -> Optional[Item]:
        row = self.conn.execute(
            "SELECT * FROM items WHERE id = ?", (item_id,)
        ).fetchone()
        return self._to_item(row) if row else None

    def get_by_name(self, name: str) -> Optional[Item]:
        row = self.conn.execute(
            "SELECT * FROM items WHERE name = ?", (name,)
        ).fetchone()
        return self._to_item(row) if row else None

    def list_all(self) -> List[Item]:
        rows = self.conn.execute("SELECT * FROM items ORDER BY id").fetchall()
        return [self._to_item(row) for row in rows]

    def delete(self, item_id: int) -> bool:
        cur = self.conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        self.conn.commit()
        return cur.rowcount > 0

    @staticmethod
    def _to_item(row: sqlite3.Row) -> Item:
        return Item(
            id=row["id"],
            name=row["name"],
            price=row["price"],
            category=row["category"],
            seller=row["seller"],
            profit_margin=row["profit_margin"],
            brand=row["brand"],
        )


class CouponRepository:
    """CRUD access to the ``coupons`` table."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add(self, coupon: Coupon) -> Coupon:
        self.conn.execute(
            "INSERT INTO coupons (code, description, discount_type, value, scope, "
            "target_category, active, max_discount, min_purchase) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                coupon.code,
                coupon.description,
                coupon.discount_type.value,
                str(coupon.value),
                coupon.scope.value,
                coupon.target_category,
                1 if coupon.active else 0,
                str(coupon.max_discount) if coupon.max_discount is not None else None,
                self._min_purchase_of(coupon),
            ),
        )
        self.conn.commit()
        return coupon

    def get_by_code(self, code: str) -> Optional[Coupon]:
        row = self.conn.execute(
            "SELECT * FROM coupons WHERE code = ?", (code,)
        ).fetchone()
        return self._to_coupon(row) if row else None

    def list_all(self) -> List[Coupon]:
        rows = self.conn.execute("SELECT * FROM coupons ORDER BY id").fetchall()
        return [self._to_coupon(row) for row in rows]

    def set_active(self, code: str, active: bool) -> bool:
        cur = self.conn.execute(
            "UPDATE coupons SET active = ? WHERE code = ?",
            (1 if active else 0, code),
        )
        self.conn.commit()
        return cur.rowcount > 0

    def delete(self, code: str) -> bool:
        cur = self.conn.execute("DELETE FROM coupons WHERE code = ?", (code,))
        self.conn.commit()
        return cur.rowcount > 0

    @staticmethod
    def _min_purchase_of(coupon: Coupon) -> Optional[str]:
        for rule in coupon.rules:
            if isinstance(rule, MinPurchase):
                return str(rule.min_value)
        return None

    @staticmethod
    def _to_coupon(row: sqlite3.Row) -> Coupon:
        min_purchase = row["min_purchase"]
        rules = [MinPurchase(min_purchase)] if min_purchase is not None else [AlwaysApplies()]
        return Coupon(
            code=row["code"],
            description=row["description"],
            discount_type=DiscountType(row["discount_type"]),
            value=row["value"],
            scope=CouponScope(row["scope"]),
            target_category=row["target_category"],
            rules=rules,
            active=bool(row["active"]),
            max_discount=row["max_discount"],
        )
