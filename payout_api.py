from flask import Flask, request, jsonify
from payout_models import (
    create_payout, get_payout, get_merchant_payouts,
    process_payout, active_payouts
)

app = Flask(__name__)


@app.route("/payouts", methods=["POST"])
def create():
    data = request.get_json()
    # BUG: no validation — missing fields cause KeyError crashes
    payout = create_payout(
        data["merchant_id"],
        data["amount"],
        data["currency"],
        data.get("memo")
    )
    return jsonify(payout), 201


@app.route("/payouts/<payout_id>", methods=["GET"])
def get(payout_id):
    p = get_payout(payout_id)
    if p is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(p), 200


@app.route("/payouts/<payout_id>/process", methods=["POST"])
def process(payout_id):
    result = process_payout(payout_id)
    if result is None:
        return jsonify({"error": "not found"}), 404
    # BUG: returns 200 even when there are processing errors
    return jsonify(result), 200


@app.route("/merchants/<merchant_id>/payouts", methods=["GET"])
def merchant_payouts(merchant_id):
    payouts = get_merchant_payouts(merchant_id)
    # BUG: doesn't return 404 for unknown merchants — returns empty list silently
    total = sum(p["amount"] for p in payouts)  # BUG: KeyError — key is 'amt' not 'amount'
    return jsonify({
        "merchant_id": merchant_id,
        "payouts": payouts,
        "total_amount": total,
        "count": len(payouts)
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
