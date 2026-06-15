"""End-to-end tests driving the CLI through ``main`` with a real SQLite file."""

from couponify.cli import main


def run(capsys, db, *args):
    """Invoke the CLI and return ``(exit_code, stdout)``."""
    code = main(["--db", db, *args])
    return code, capsys.readouterr().out


def test_add_item_then_list(capsys, db_path):
    code, out = run(capsys, db_path, "add-item", "--name", "Phone",
                    "--price", "100", "--category", "tech", "--seller", "store")
    assert code == 0
    assert "Item cadastrado com id 1" in out

    code, out = run(capsys, db_path, "list-items")
    assert code == 0
    assert "Phone" in out


def test_list_items_empty(capsys, db_path):
    code, out = run(capsys, db_path, "list-items")
    assert code == 0
    assert "Nenhum item" in out


def test_add_to_cart_and_show(capsys, db_path):
    run(capsys, db_path, "add-item", "--name", "Phone", "--price", "100",
        "--category", "tech", "--seller", "store")
    code, out = run(capsys, db_path, "add-to-cart", "--item-id", "1", "--quantity", "2")
    assert code == 0
    assert "2x Phone" in out

    code, out = run(capsys, db_path, "show-cart")
    assert "2x Phone" in out


def test_checkout_without_coupon(capsys, db_path):
    run(capsys, db_path, "add-item", "--name", "Phone", "--price", "100",
        "--category", "tech", "--seller", "store")
    run(capsys, db_path, "add-to-cart", "--item-id", "1")
    code, out = run(capsys, db_path, "checkout")
    assert code == 0
    assert "Subtotal: R$ 100.00" in out
    assert "Total: R$ 100.00" in out


def test_apply_invalid_coupon_fails(capsys, db_path):
    code, out = run(capsys, db_path, "apply-coupon", "--code", "NOPE")
    assert code == 1
    assert "invalido ou inexistente" in out


def test_add_to_cart_unknown_item_fails(capsys, db_path):
    code, out = run(capsys, db_path, "add-to-cart", "--item-id", "42")
    assert code == 1
    assert "nao encontrado" in out


def test_state_persists_across_invocations(capsys, db_path):
    run(capsys, db_path, "add-item", "--name", "Phone", "--price", "100",
        "--category", "tech", "--seller", "store")
    run(capsys, db_path, "add-to-cart", "--item-id", "1")
    # Fresh process / fresh service, same database file.
    code, out = run(capsys, db_path, "show-cart")
    assert "1x Phone" in out


def test_clear_cart(capsys, db_path):
    run(capsys, db_path, "add-item", "--name", "Phone", "--price", "100",
        "--category", "tech", "--seller", "store")
    run(capsys, db_path, "add-to-cart", "--item-id", "1")
    code, out = run(capsys, db_path, "clear-cart")
    assert "esvaziado" in out
    _, out = run(capsys, db_path, "show-cart")
    assert "vazio" in out
