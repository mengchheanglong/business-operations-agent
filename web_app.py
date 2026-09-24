"""
Web interface for AI Small Business Operations Agent.
Run with: python web_app.py
Open http://localhost:5000 in your browser.
"""

import os
import sys
import json
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent import AIBusinessAgent

app = Flask(__name__)
agent = AIBusinessAgent()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/process", methods=["POST"])
def process_order():
    data = request.json
    message = data.get("message", "")
    customer = data.get("customer", "Customer")

    if not message:
        return jsonify({"error": "No message provided"}), 400

    result = agent.process_order(message, customer)
    return jsonify(result)


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "deepseek_configured": bool(os.environ.get("DEEPSEEK_API_KEY")),
        "telegram_configured": bool(os.environ.get("TELEGRAM_BOT_TOKEN")),
        "sheets_configured": bool(os.environ.get("GOOGLE_SHEET_ID")),
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
