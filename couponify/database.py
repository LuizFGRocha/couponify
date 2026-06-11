"""SQLite connection and schema management.

The database keeps the registered items and coupons plus a single shared cart
(its lines and applied coupons), so the CLI behaves consistently across separate
invocations.
"""

from __future__ import annotations

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    price         TEXT    NOT NULL,
    category      TEXT    NOT NULL,
    seller        TEXT    NOT NULL,
    profit_margin REAL    NOT NULL DEFAULT 0,
    brand         TEXT    NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS coupons (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    code            TEXT    NOT NULL UNIQUE,
    description     TEXT    NOT NULL DEFAULT '',
    discount_type   TEXT    NOT NULL,
    value           TEXT    NOT NULL,
    scope           TEXT    NOT NULL,
    target_category TEXT,
    active          INTEGER NOT NULL DEFAULT 1,
    max_discount    TEXT,
    min_purchase    TEXT
);

CREATE TABLE IF NOT EXISTS cart_items (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id  INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (item_id) REFERENCES items (id)
);

CREATE TABLE IF NOT EXISTS cart_coupons (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    coupon_code TEXT    NOT NULL UNIQUE
);
"""


def connect(db_path: str) -> sqlite3.Connection:
    """Open a connection with row access by column name and FK enforcement."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    """Create all tables if they do not exist yet."""
    conn.executescript(SCHEMA)
    conn.commit()
