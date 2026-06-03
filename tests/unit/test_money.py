"""Unit tests for the money helpers."""

from decimal import Decimal

import pytest

from couponify.money import ZERO, clamp_non_negative, money


def test_money_from_string():
    assert money("10.5") == Decimal("10.50")


def test_money_from_int():
    assert money(7) == Decimal("7.00")


def test_money_from_float_avoids_binary_noise():
    assert money(0.1) == Decimal("0.10")


def test_money_quantizes_to_two_places():
    assert money("3.333") == Decimal("3.33")


def test_money_rounds_half_up():
    assert money("0.125") == Decimal("0.13")


def test_money_negative_is_preserved():
    assert money("-5") == Decimal("-5.00")


def test_zero_constant():
    assert ZERO == Decimal("0.00")


def test_clamp_non_negative_keeps_positive():
    assert clamp_non_negative(money("4.20")) == Decimal("4.20")


def test_clamp_non_negative_floors_negative():
    assert clamp_non_negative(money("-1")) == ZERO


def test_clamp_non_negative_on_zero():
    assert clamp_non_negative(ZERO) == ZERO


@pytest.mark.parametrize("value,expected", [
    ("1", "1.00"),
    ("1.005", "1.01"),
    ("2.994", "2.99"),
])
def test_money_parametrized(value, expected):
    assert money(value) == Decimal(expected)
