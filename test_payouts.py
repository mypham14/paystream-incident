import pytest
from payout_models import (
    create_payout, get_payout, process_payout,
    calculate_fee, get_merchant_payouts, active_payouts
)
from payout_api import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def clear_payouts():
    active_payouts.clear()
    yield
    active_payouts.clear()


# --- Model Tests ---

def test_create_payout():
    p = create_payout("M001", 100.00, "USD")
    assert p["merchant_id"] == "M001"
    assert p["amt"] == 100.00
    assert p["status"] == "PENDING"


def test_calculate_fee_usd():
    fee = calculate_fee(100.00, "USD")
    assert fee == 3.20  # 100 * 0.029 + 0.30 = 3.20


def test_calculate_fee_eur():
    fee = calculate_fee(100.00, "EUR")
    assert fee == 4.00  # 100 * 0.035 + 0.50 = 4.00


def test_process_payout():
    p = create_payout("M001", 250.00, "USD")
    result = process_payout(p["id"])
    assert result["status"] == "COMPLETED"
    assert result["net_amount"] == 250.00 - result["fee"]


def test_process_nonexistent_payout():
    result = process_payout("fake-id-12345")
    assert result is None


# --- API Tests ---

def test_api_create_payout(client):
    resp = client.post("/payouts", json={
        "merchant_id": "M100",
        "amount": 500.00,
        "currency": "USD"
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["amt"] == 500.00


def test_api_get_payout(client):
    resp = client.post("/payouts", json={
        "merchant_id": "M100",
        "amount": 200.00,
        "currency": "USD"
    })
    payout_id = resp.get_json()["id"]
    resp2 = client.get(f"/payouts/{payout_id}")
    assert resp2.status_code == 200


def test_api_merchant_payouts(client):
    client.post("/payouts", json={"merchant_id": "M200", "amount": 100.00, "currency": "USD"})
    client.post("/payouts", json={"merchant_id": "M200", "amount": 200.00, "currency": "USD"})
    resp = client.get("/merchants/M200/payouts")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] == 2
    assert data["total_amount"] == 300.00  # FAILS: KeyError on 'amount' — key is 'amt'


def test_api_missing_fields(client):
    resp = client.post("/payouts", json={"merchant_id": "M300"})
    # FAILS: expects 400 but gets 500 (unhandled KeyError)
    assert resp.status_code == 400
