# PayPilot — 3-Minute Demo Video Script

**Target:** < 3:00 · **Format:** screen recording + voiceover · **Upload:** YouTube (public)

---

### 0:00–0:20 — The problem (20s)
> "Online checkout is still a maze: search, filter, compare tabs, forms,
> redirects. What if you could just *tell* an AI what you want — and it
> handles the entire PayPal checkout for you? Meet **PayPilot**."

*[Show the PayPilot chat UI loading.]*

### 0:20–1:00 — Live demo, part 1: discovery (40s)
> "I need wireless headphones under $100."

*[Type it. Bot returns 3 ranked matches with prices.]*
> "PayPilot understood the product *and* the budget constraint, and ranked
> real catalog items. I pick number one."

*[Type "1". Bot confirms the pick with details.]*

### 1:00–2:00 — Live demo, part 2: PayPal checkout (60s)
> "I say yes — and PayPilot calls the **PayPal Sandbox Orders API** to
> create a real order."

*[Type "yes". Bot shows order ID + approval link. Click the link —
show the PayPal Sandbox approval page. Approve.]*
> "That's a genuine PayPal order — intent CAPTURE — created programmatically.
> I approve it in the sandbox, type *done*…"

*[Type "done". Bot captures and shows the receipt.]*
> "…and the payment is captured. Full conversational checkout, zero forms."

### 2:00–2:40 — How it's built (40s)
> "Under the hood: a Python/Flask backend, a state-machine agent that
> orchestrates intent → match → order → capture, and PayPal's REST Orders
> v2 API. The agent layer is model-agnostic — any LLM can plug in.
> Sandbox mode means judges can run the entire flow with zero setup."

*[Quick scroll through `agent.py` and `paypal_client.py` in the editor.]*

### 2:40–3:00 — Close (20s)
> "PayPilot: tell it what you want, it checks you out with PayPal.
> Built for the PayPal AI Hackathon 2026 — agentic commerce, done right."

*[End card: repo URL + "PayPilot — AI Agentic Checkout".]*

---

**Recording notes:** 1080p, system audio off, voiceover in English,
no copyrighted music, no third-party trademarks on screen.
