# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from .db import init_db, get_conn
from .crud import create_order, list_orders, get_order, update_order, delete_order
from .schemas import OrderCreate, OrderUpdate, OrderInDB
from .sentry_integration import init_sentry
import sentry_sdk
import uvicorn
import os

# Initialize DB
init_db()

# Initialize Sentry (safe to call once)
init_sentry()

# Create FastAPI app
app = FastAPI(title="Mini Orders API")

@app.post("/orders", response_model=OrderInDB, status_code=201)
def api_create_order(payload: OrderCreate):
    try:
        return create_order(
            payload.customer_name,
            payload.items,
            payload.total_amount
        )
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="internal error creating order")

@app.get("/orders")
def api_list_orders(limit: int = 100):
    return list_orders(limit)

@app.get("/orders/{order_id}", response_model=OrderInDB)
def api_get_order(order_id: int):
    o = get_order(order_id)
    if not o:
        raise HTTPException(status_code=404, detail="order not found")
    return o

@app.patch("/orders/{order_id}", response_model=OrderInDB)
def api_update_order(order_id: int, payload: OrderUpdate):
    o = update_order(
        order_id,
        status=payload.status,
        items=payload.items,
        total_amount=payload.total_amount
    )
    if not o:
        raise HTTPException(status_code=404, detail="order not found")
    return o

@app.delete("/orders/{order_id}")
def api_delete_order(order_id: int):
    ok = delete_order(order_id)
    if not ok:
        raise HTTPException(status_code=404, detail="order not found")
    return {"deleted": ok}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    conn = get_conn()
    row = conn.execute("SELECT COUNT(*) as cnt FROM orders").fetchone()
    return {"orders_count": int(row["cnt"])}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000))
    )

