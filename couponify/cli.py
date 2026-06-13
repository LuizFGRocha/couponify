"""Command line interface.

Thin layer over :class:`~couponify.service.CouponifyService`. ``main`` is written
so it can be driven from tests: it accepts an explicit argv, supports an
injectable database path (``--db`` or the ``COUPONIFY_DB`` env var) and returns a
process exit code. User-facing messages are in Portuguese.
"""

from __future__ import annotations

import argparse
import os
from decimal import Decimal
from typing import List, Optional, Sequence

from .models import Coupon, CouponScope, DiscountType
from .rules import MinPurchase
from .service import CouponifyService

DEFAULT_DB = "couponify.db"


def _format_money(value: Decimal) -> str:
    return f"R$ {value:.2f}"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="couponify",
        description="Simulador de carrinho de compras com descontos dinamicos.",
    )
    parser.add_argument(
        "--db",
        default=os.environ.get("COUPONIFY_DB", DEFAULT_DB),
        help="Caminho do banco SQLite (padrao: %(default)s).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_item = sub.add_parser("add-item", help="Cadastra um item.")
    p_item.add_argument("--name", required=True)
    p_item.add_argument("--price", required=True)
    p_item.add_argument("--category", required=True)
    p_item.add_argument("--seller", required=True)
    p_item.add_argument("--margin", type=float, default=0.0)
    p_item.add_argument("--brand", default="")

    sub.add_parser("list-items", help="Lista os itens cadastrados.")

    p_coupon = sub.add_parser("add-coupon", help="Cadastra um cupom.")
    p_coupon.add_argument("--code", required=True)
    p_coupon.add_argument("--type", required=True, choices=["percentage", "fixed"])
    p_coupon.add_argument("--value", required=True)
    p_coupon.add_argument("--description", default="")
    p_coupon.add_argument("--scope", choices=["cart", "item"], default="cart")
    p_coupon.add_argument("--target-category", dest="target_category")
    p_coupon.add_argument("--min-purchase", dest="min_purchase")
    p_coupon.add_argument("--max-discount", dest="max_discount")
    p_coupon.add_argument("--inactive", action="store_true")

    sub.add_parser("list-coupons", help="Lista os cupons cadastrados.")

    p_add = sub.add_parser("add-to-cart", help="Adiciona um item ao carrinho.")
    p_add.add_argument("--item-id", dest="item_id", type=int, required=True)
    p_add.add_argument("--quantity", type=int, default=1)

    sub.add_parser("show-cart", help="Mostra o conteudo do carrinho.")

    p_apply = sub.add_parser("apply-coupon", help="Aplica um cupom ao carrinho.")
    p_apply.add_argument("--code", required=True)

    sub.add_parser("clear-cart", help="Esvazia o carrinho.")
    sub.add_parser("checkout", help="Calcula subtotal, desconto e total.")
    return parser


def _cmd_add_item(service: CouponifyService, args) -> int:
    item = service.add_item(
        name=args.name, price=args.price, category=args.category,
        seller=args.seller, profit_margin=args.margin, brand=args.brand,
    )
    print(f"Item cadastrado com id {item.id}: {item.name} ({_format_money(item.price)})")
    return 0


def _cmd_list_items(service: CouponifyService, args) -> int:
    items = service.list_items()
    if not items:
        print("Nenhum item cadastrado.")
        return 0
    for item in items:
        print(f"[{item.id}] {item.name} - {_format_money(item.price)} "
              f"- categoria: {item.category} - vendedor: {item.seller}")
    return 0


def _cmd_add_coupon(service: CouponifyService, args) -> int:
    scope = CouponScope.ITEM if args.scope == "item" else CouponScope.WHOLE_CART
    rules = [MinPurchase(args.min_purchase)] if args.min_purchase is not None else None
    coupon = Coupon(
        code=args.code,
        discount_type=DiscountType(args.type),
        value=args.value,
        description=args.description,
        scope=scope,
        target_category=args.target_category,
        rules=rules if rules else None,
        active=not args.inactive,
        max_discount=args.max_discount,
    )
    service.add_coupon(coupon)
    print(f"Cupom cadastrado: {coupon.code}")
    return 0


def _cmd_list_coupons(service: CouponifyService, args) -> int:
    coupons = service.list_coupons()
    if not coupons:
        print("Nenhum cupom cadastrado.")
        return 0
    for coupon in coupons:
        status = "ativo" if coupon.active else "inativo"
        print(f"{coupon.code} - {coupon.discount_type.value} {coupon.value} "
              f"- escopo: {coupon.scope.value} - {status}")
    return 0


def _cmd_add_to_cart(service: CouponifyService, args) -> int:
    try:
        item = service.add_to_cart(args.item_id, args.quantity)
    except LookupError:
        print(f"Item {args.item_id} nao encontrado.")
        return 1
    print(f"Adicionado ao carrinho: {args.quantity}x {item.name}")
    return 0


def _cmd_show_cart(service: CouponifyService, args) -> int:
    cart = service.build_cart()
    if cart.is_empty():
        print("Carrinho vazio.")
        return 0
    for line in cart.items:
        print(f"{line.quantity}x {line.item.name} - {_format_money(line.subtotal)}")
    for coupon in cart.coupons:
        print(f"Cupom aplicado: {coupon.code}")
    return 0


def _cmd_apply_coupon(service: CouponifyService, args) -> int:
    if not service.apply_coupon_to_cart(args.code):
        print(f"Cupom {args.code} invalido ou inexistente.")
        return 1
    print(f"Cupom {args.code} aplicado ao carrinho.")
    return 0


def _cmd_clear_cart(service: CouponifyService, args) -> int:
    service.clear_cart()
    print("Carrinho esvaziado.")
    return 0


def _cmd_checkout(service: CouponifyService, args) -> int:
    cart = service.build_cart()
    print(f"Subtotal: {_format_money(cart.subtotal())}")
    print(f"Desconto: {_format_money(cart.total_discount())}")
    print(f"Total: {_format_money(cart.total())}")
    return 0


_COMMANDS = {
    "add-item": _cmd_add_item,
    "list-items": _cmd_list_items,
    "add-coupon": _cmd_add_coupon,
    "list-coupons": _cmd_list_coupons,
    "add-to-cart": _cmd_add_to_cart,
    "show-cart": _cmd_show_cart,
    "apply-coupon": _cmd_apply_coupon,
    "clear-cart": _cmd_clear_cart,
    "checkout": _cmd_checkout,
}


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Entry point. Returns the process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    service = CouponifyService(args.db)
    try:
        return _COMMANDS[args.command](service, args)
    except ValueError as exc:
        print(f"Erro: {exc}")
        return 1
    finally:
        service.close()


def run() -> None:  # console_scripts entry point
    raise SystemExit(main())
