# app/crud.py
import json
from typing import List, Optional
from .db import get_conn

def create_order(customer_name: str, items: List[str], total_amount: float) -> dict:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (customer_name, items, total_amount) VALUES (?, ?, ?)",
        (customer_name, json.dumps(items), total_amount),
    )
    conn.commit()
    oid = cur.lastrowid
    row = conn.execute("SELECT * FROM orders WHERE id = ?", (oid,)).fetchone()
    return _row_to_dict(row)

def list_orders(limit: int = 100) -> List[dict]:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    return [_row_to_dict(r) for r in rows]

def get_order(order_id: int) -> Optional[dict]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    return _row_to_dict(row) if row else None

def update_order(order_id: int, status=None, items=None, total_amount=None) -> Optional[dict]:
    conn = get_conn()
    # get current
    current = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not current:
        return None
    import json
    new_status = status if status is not None else current["status"]
    new_items = json.dumps(items) if items is not None else current["items"]
    new_total = total_amount if total_amount is not None else current["total_amount"]
    conn.execute(
        "UPDATE orders SET status = ?, items = ?, total_amount = ? WHERE id = ?",
        (new_status, new_items, new_total, order_id)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    return _row_to_dict(row)

def delete_order(order_id: int) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    return cur.rowcount > 0

def _row_to_dict(row):
    if row is None:
        return None
    import json
    return {
        "id": row["id"],
        "customer_name": row["customer_name"],
        "items": json.loads(row["items"]) if isinstance(row["items"], str) else row["items"],
        "status": row["status"],
        "total_amount": float(row["total_amount"]),
        "created_at": row["created_at"],
    }
