import datetime
import uuid

# PayStream Payout Models - v3.1

active_payouts = []

def create_payout(merchant_id, amount, currency, memo=None):
    if merchant_id is None or not str(merchant_id).strip():
        raise ValueError("merchant_id is required")

    try:
        amount_value = float(amount)
    except (TypeError, ValueError):
        raise ValueError("amount must be a number")

    if amount_value <= 0:
        raise ValueError("amount must be greater than 0")

    if currency is None or not str(currency).strip():
        raise ValueError("currency is required")

    payout = {
        "id": str(uuid.uuid4()),
        "merchant_id": merchant_id,
        "amount": amount_value,
        "currency": currency,
        "memo": memo,
        "status": "PENDING",
        "created_at": str(datetime.datetime.now()),
        "processed_at": None
    }
    active_payouts.append(payout)
    return payout


def get_payout(payout_id):
    for p in active_payouts:
        if p["id"] == payout_id:
            return p
    return None


def get_merchant_payouts(merchant_id):
    result = []
    for p in active_payouts:
        if p["merchant_id"] == merchant_id:
            result.append(p)
    return result


def process_payout(payout_id):
    p = get_payout(payout_id)
    if p is None:
        return None

    try:
        fee = calculate_fee(p["amount"], p["currency"])
    except ValueError as exc:
        raise ValueError(f"Unable to process payout {payout_id}: {exc}") from exc

    p["fee"] = fee
    p["net_amount"] = p["amount"] - fee
    p["status"] = "COMPLETED"
    p["processed_at"] = str(datetime.datetime.now())
    return p


def calculate_fee(amount, currency):
    # Fee schedule: 2.9% + $0.30 for USD, 3.5% + €0.50 for EUR
    if currency == "USD":
        return round(amount * 0.029 + 0.30, 2)
    elif currency == "EUR":
        return round(amount * 0.035 + 0.50, 2)
    raise ValueError(f"Unsupported currency: {currency}")
