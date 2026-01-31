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
app = FastAPI(
    title="Mini Orders API",
    servers=[{"url": "http://localhost:8000", "description": "Local Development"}]
)

# Add CORS Middleware to allow browser usage (Swagger UI)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Sentry debug endpoint - triggers a real exception for testing
@app.get("/sentry-debug")
async def trigger_error():
    print("⚠️ [DEBUG] Triggering ZeroDivisionError via API Request ⚠️")
    division_by_zero = 1 / 0
    return {"this": "will never return"}

# ============================================
# REALISTIC ERROR SCENARIOS FOR SENTRY TESTING
# ============================================

@app.get("/error/database")
def simulate_database_error():
    """Simulates a database connection failure - common in production"""
    raise ConnectionError("Database connection failed: Unable to connect to PostgreSQL at db.example.com:5432")

@app.get("/error/null-pointer")
def simulate_null_pointer():
    """Simulates accessing data from a None object - very common bug"""
    user = None
    # This will raise AttributeError: 'NoneType' object has no attribute 'name'
    return {"username": user.name}

@app.get("/error/key-missing")
def simulate_key_error():
    """Simulates missing key in API response - happens when external API changes"""
    api_response = {"id": 123, "status": "active"}
    # This key doesn't exist - KeyError
    return {"email": api_response["email"]}

@app.get("/error/timeout")
def simulate_timeout():
    """Simulates an external service timeout"""
    import time
    # Simulating a slow external API call that times out
    raise TimeoutError("Request to payment gateway timed out after 30 seconds")

@app.get("/error/value")
def simulate_value_error():
    """Simulates invalid data processing - common in data pipelines"""
    price = "not-a-number"
    # This will raise ValueError
    total = float(price) * 1.18  # trying to calculate tax
    return {"total": total}

@app.get("/error/permission")
def simulate_permission_error():
    """Simulates unauthorized access attempt"""
    raise PermissionError("User 'guest' does not have permission to access /admin/settings")

@app.get("/error/file-not-found")
def simulate_file_error():
    """Simulates missing configuration file"""
    with open("/etc/app/missing-config.yaml", "r") as f:
        return {"config": f.read()}

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

