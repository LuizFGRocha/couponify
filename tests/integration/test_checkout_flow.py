"""End-to-end checkout flows combining items and coupons through the CLI."""

from couponify.cli import main


def run(capsys, db, *args):
    code = main(["--db", db, *args])
    return code, capsys.readouterr().out


def _seed_phone(capsys, db, price="100"):
    run(capsys, db, "add-item", "--name", "Phone", "--price", price,
        "--category", "tech", "--seller", "store")


def test_percentage_coupon_flow(capsys, db_path):
    _seed_phone(capsys, db_path)
    run(capsys, db_path, "add-to-cart", "--item-id", "1")
    run(capsys, db_path, "add-coupon", "--code", "OFF10",
        "--type", "percentage", "--value", "10")
    run(capsys, db_path, "apply-coupon", "--code", "OFF10")
    code, out = run(capsys, db_path, "checkout")
    assert code == 0
    assert "Desconto: R$ 10.00" in out
    assert "Total: R$ 90.00" in out


def test_fixed_coupon_flow(capsys, db_path):
    _seed_phone(capsys, db_path)
    run(capsys, db_path, "add-to-cart", "--item-id", "1")
    run(capsys, db_path, "add-coupon", "--code", "MINUS25",
        "--type", "fixed", "--value", "25")
    run(capsys, db_path, "apply-coupon", "--code", "MINUS25")
    code, out = run(capsys, db_path, "checkout")
    assert "Total: R$ 75.00" in out


def test_item_scope_coupon_flow(capsys, db_path):
    run(capsys, db_path, "add-item", "--name", "Book", "--price", "50",
        "--category", "books", "--seller", "store")
    run(capsys, db_path, "add-item", "--name", "Phone", "--price", "100",
        "--category", "tech", "--seller", "store")
    run(capsys, db_path, "add-to-cart", "--item-id", "1")
    run(capsys, db_path, "add-to-cart", "--item-id", "2")
    run(capsys, db_path, "add-coupon", "--code", "BOOKS20", "--type", "percentage",
        "--value", "20", "--scope", "item", "--target-category", "books")
    run(capsys, db_path, "apply-coupon", "--code", "BOOKS20")
    code, out = run(capsys, db_path, "checkout")
    # 20% off the 50.00 of books only -> 10.00 discount on a 150.00 subtotal.
    assert "Subtotal: R$ 150.00" in out
    assert "Desconto: R$ 10.00" in out
    assert "Total: R$ 140.00" in out
