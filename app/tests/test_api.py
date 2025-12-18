# app/tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def test_create_and_get_order():
    payload = {"customer_name":"Bob","items":["pepperoni"],"total_amount":9.5}
    r = client.post("/orders", json=payload)
    assert r.status_code == 201
    body = r.json()
    oid = body["id"]
    assert body["customer_name"] == "Bob"

    r2 = client.get(f"/orders/{oid}")
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["id"] == oid

def test_list_orders():
    r = client.get("/orders?limit=5")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
