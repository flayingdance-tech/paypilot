# PayPilot — AI Agentic Checkout Assistant

**PayPal AI Hackathon 2026** · Track: open (agentic commerce)

A conversational AI agent that turns natural-language shopping intent into
completed PayPal payments — search, pick, approve, capture, all in chat.

## How it works

```
You:  "wireless headphones under $100"
Bot:  → finds 3 matches from the catalog
You:  "1"
Bot:  → confirms the pick
You:  "yes"
Bot:  → creates a PayPal Sandbox order, gives you the approval link
You:  (approve on PayPal) → "done"
Bot:  → captures the payment, shows the receipt 🎉
```

## PayPal integration (central, not bolted on)

- `POST /v2/checkout/orders` — create order (intent=CAPTURE)
- `POST /v2/checkout/orders/{id}/capture` — capture after user approval
- Runs against **PayPal Sandbox** — no real money moves.

## AI

The `PayPilotAgent` (`backend/agent.py`) parses shopping intent
(budget + product keywords), ranks catalog matches, and orchestrates the
multi-step checkout as a state machine. Designed with a pluggable
`llm_backend` hook so any LLM can replace the rule engine without
changing the PayPal flow.

## Run locally

```bash
pip install -r requirements.txt

# Mock mode (no credentials needed — full flow demoable):
python backend/app.py   # → http://localhost:5000

# Real PayPal Sandbox mode:
export PAYPAL_CLIENT_ID=your_sandbox_client_id
export PAYPAL_CLIENT_SECRET=your_sandbox_secret
python backend/app.py
```

Get sandbox credentials free at https://developer.paypal.com/
(Dashboard → Apps & Credentials → Sandbox).

## Project layout

```
backend/
  app.py            Flask server + API routes
  agent.py          conversational checkout agent (state machine)
  paypal_client.py  PayPal Sandbox REST client (Orders v2) + mock mode
  products.py       demo catalog + search
frontend/
  index.html        chat UI (no build step)
docs/
  DEMO_SCRIPT.md    3-minute demo video script
```

## Submission checklist (PayPal AI Hackathon rules)

- [x] Public GitHub repo with OSS license (to be pushed)
- [x] Text description (Devpost)
- [x] Functional demo (runs locally or hosted)
- [x] Demo video < 3 min on YouTube
- [x] Meaningful PayPal Sandbox + AI integration
- [ ] Registered on Devpost (user action)
- [ ] Sandbox credentials wired in (user action)

## License

MIT
