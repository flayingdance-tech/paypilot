"""PayPilot — AI Agentic Commerce Assistant for PayPal AI Hackathon 2026.

A conversational AI agent that turns natural-language shopping intent into
completed PayPal payments:

  User: "I need wireless headphones under $100"
  PayPilot: finds matches -> user picks -> creates PayPal order ->
            user approves -> captures payment. All in chat.

PayPal integration: Sandbox Orders API v2 (create + capture).
AI: conversational intent parsing + product matching + checkout orchestration.
     The agent layer is model-agnostic (pluggable LLM backend).
"""
import os
from flask import Flask, request, jsonify, send_from_directory
from agent import PayPilotAgent
from paypal_client import PayPalClient

app = Flask(__name__, static_folder="../frontend", static_url_path="")

# PayPal sandbox credentials come from env (user provides after signup).
# Without them, the client runs in MOCK mode for local development.
paypal = PayPalClient(
    client_id=os.environ.get("PAYPAL_CLIENT_ID"),
    client_secret=os.environ.get("PAYPAL_CLIENT_SECRET"),
    sandbox=True,
)
agent = PayPilotAgent(paypal)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"text": "I couldn't understand that request. "
                                "Try again?"}), 400
    try:
        reply = agent.handle(data.get("session_id", "demo"),
                             data.get("message", ""))
    except Exception as e:  # never leak stack traces to the client
        app.logger.exception("chat handler failed")
        return jsonify({"text": "Something went wrong on my end — "
                                "let's try that again."}), 500
    return jsonify(reply)


@app.route("/api/health")
def health():
    return jsonify({"ok": True,
                    "paypal_mode": paypal.mode,
                    "agent": "paypilot-v1"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)),
            debug=False)
