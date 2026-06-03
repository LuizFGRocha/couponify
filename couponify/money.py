"""Money helpers.

Monetary values are represented as :class:`decimal.Decimal` quantized to two
decimal places. Using ``Decimal`` (instead of ``float``) keeps the arithmetic
exact, which matters for a discount engine and makes property-based testing
meaningful.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Union

Number = Union[int, float, str, Decimal]

CENTS = Decimal("0.01")


def money(value: Number) -> Decimal:
    """Return ``value`` as a ``Decimal`` quantized to two decimal places.

    Floats are converted through ``str`` first to avoid binary rounding noise
    (e.g. ``0.1`` becoming ``0.1000000000000000055...``).
    """
    if isinstance(value, float):
        value = str(value)
    return Decimal(value).quantize(CENTS, rounding=ROUND_HALF_UP)


ZERO = money(0)


def clamp_non_negative(value: Decimal) -> Decimal:
    """Return ``value`` unless it is negative, in which case return zero."""
    return value if value > ZERO else ZERO
