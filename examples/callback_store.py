"""Example-only fixed positive payment inbox/outbox; no fulfillment worker.

Set BEPUSDT_EXAMPLE_DB to a writable absolute path outside your repository.
The application owns backup, workers, reconciliation and production storage.
"""

import json
import sqlite3
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
from pathlib import Path

SCHEMA = """
    CREATE TABLE IF NOT EXISTS intents (order_id TEXT PRIMARY KEY, amount TEXT NOT NULL, fiat TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS attempts (
        trade_id TEXT PRIMARY KEY, order_id TEXT NOT NULL, actual_amount TEXT NOT NULL, token TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS inbox (
        trade_id TEXT NOT NULL, status INTEGER NOT NULL, payload TEXT NOT NULL, UNIQUE(trade_id, status, payload));
    CREATE TABLE IF NOT EXISTS outbox (order_id TEXT PRIMARY KEY, payload TEXT NOT NULL);
"""


def _positive(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError("expected fixed positive amount")
    amount = Decimal(str(value))
    if not amount.is_finite() or amount <= 0:
        raise ValueError("expected fixed positive amount")
    return amount


class CallbackStore:
    """Record intent before creation, returned attempts, and verified callbacks."""

    def __init__(self, path):
        self.path = str(path) if path else None
        if self.path:
            candidate = Path(self.path)
            repository = Path(__file__).resolve().parents[1]
            if (
                not candidate.is_absolute()
                or repository == candidate.resolve()
                or repository in candidate.resolve().parents
            ):
                raise ValueError("example state must use an absolute path outside the repository")

    @contextmanager
    def _connect(self):
        if not self.path:
            raise RuntimeError("configure BEPUSDT_EXAMPLE_DB outside the repository")
        conn = sqlite3.connect(self.path, timeout=10)
        try:
            conn.executescript(SCHEMA)
            with conn:
                yield conn
        finally:
            conn.close()

    def _intent(self, conn, order_id, amount, fiat):
        amount = _positive(amount)
        if not isinstance(order_id, str) or not order_id or fiat not in ("CNY", "USD", "EUR", "GBP", "JPY"):
            raise ValueError("invalid business intent")
        previous = conn.execute("SELECT amount, fiat FROM intents WHERE order_id=?", (order_id,)).fetchone()
        if previous and (_positive(previous[0]) != amount or previous[1] != fiat):
            raise ValueError("business amount or fiat changed")
        conn.execute("INSERT OR IGNORE INTO intents VALUES (?, ?, ?)", (order_id, str(amount), fiat))

    def reserve(self, order_id, amount, fiat="CNY"):
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            self._intent(conn, order_id, amount, fiat)

    def register(self, order):
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            self._intent(conn, order.order_id, order.amount_text or order.amount, order.fiat or "CNY")
            actual = _positive(order.actual_amount_text or order.actual_amount)
            if (
                not isinstance(order.trade_id, str)
                or not order.trade_id
                or not isinstance(order.token, str)
                or not order.token
            ):
                raise ValueError("unallocated attempt")
            previous = conn.execute("SELECT order_id FROM attempts WHERE trade_id=?", (order.trade_id,)).fetchone()
            if previous and previous[0] != order.order_id:
                raise ValueError("trade belongs to another business intent")
            conn.execute(
                """INSERT INTO attempts VALUES (?, ?, ?, ?)
                ON CONFLICT(trade_id) DO UPDATE SET actual_amount=excluded.actual_amount, token=excluded.token""",
                (order.trade_id, order.order_id, str(actual), order.token),
            )

    def accept(self, data):
        """Call only after verify_callback; false means reject, storage errors propagate."""
        if not isinstance(data, dict):
            return False
        trade_id, order_id, status = data.get("trade_id"), data.get("order_id"), data.get("status")
        if (
            not isinstance(trade_id, str)
            or not isinstance(order_id, str)
            or type(status) is not int
            or status not in range(1, 7)
        ):
            return False
        try:
            amount, actual = _positive(data.get("amount")), _positive(data.get("actual_amount"))
        except (ValueError, InvalidOperation):
            return False
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                """SELECT a.order_id, i.amount, i.fiat, a.actual_amount, a.token
                FROM attempts a JOIN intents i ON i.order_id=a.order_id WHERE trade_id=?""",
                (trade_id,),
            ).fetchone()
            if not row or row[0] != order_id or _positive(row[1]) != amount or _positive(row[3]) != actual:
                return False
            if data.get("token") != row[4] or ("fiat" in data and data["fiat"] != row[2]):
                return False
            if status == 2 and (
                not isinstance(data.get("block_transaction_id"), str) or not data["block_transaction_id"]
            ):
                return False
            payload = json.dumps(
                {k: v for k, v in data.items() if k != "signature"}, ensure_ascii=False, sort_keys=True
            )
            conn.execute("INSERT OR IGNORE INTO inbox VALUES (?, ?, ?)", (trade_id, status, payload))
            if status == 2:
                # A worker processes this unique business-order task with its own delivery idempotency.
                conn.execute("INSERT OR IGNORE INTO outbox VALUES (?, ?)", (order_id, payload))
        return True
