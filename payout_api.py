from flask import Flask, request, jsonify
from payout_models import (
    create_payout, get_payout, get_merchant_payouts,
    process_payout, active_payouts
)

app = Flask(__name__)


@app.route("/payouts", methods=["POST"])
def create():
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({"error": "Request JSON body is required"}), 400

    try:
        payout = create_payout(
            data.get("merchant_id"),
            data.get("amount"),
            data.get("currency"),
            data.get("memo")
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(payout), 201


@app.route("/payouts/<payout_id>", methods=["GET"])
def get(payout_id):
    p = get_payout(payout_id)
    if p is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(p), 200


@app.route("/payouts/<payout_id>/process", methods=["POST"])
def process(payout_id):
    try:
        result = process_payout(payout_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if result is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(result), 200


@app.route("/merchants/<merchant_id>/payouts", methods=["GET"])
def merchant_payouts(merchant_id):
    payouts = get_merchant_payouts(merchant_id)
    total = sum(p["amount"] for p in payouts)
    return jsonify({
        "merchant_id": merchant_id,
        "payouts": payouts,
        "total_amount": total,
        "count": len(payouts)
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
