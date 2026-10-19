"""PayPilot conversational agent.

Turns natural-language shopping intent into a PayPal checkout:
  intent parse -> product match -> confirm -> create order ->
  approval link -> capture -> receipt.

The intent parser here is a transparent rule/template engine so the whole
flow is auditable offline. In production it is designed to sit behind any
LLM via the `llm_backend` hook (see AgentConfig).
"""
import re
import uuid
from products import CATALOG, search


class PayPilotAgent:
    def __init__(self, paypal_client, base_url="http://localhost:5000"):
        self.paypal = paypal_client
        self.base_url = base_url.rstrip("/")
        self.sessions = {}  # session_id -> {state, shortlist, pending}

    # ---- main entry -----------------------------------------------------
    def handle(self, session_id, message):
        s = self.sessions.setdefault(session_id, {"state": "idle"})
        text = (message or "").strip()
        low = text.lower()

        if re.search(r"\b(hi|hello|hey|start)\b", low) and s["state"] == "idle":
            return self._say(
                "👋 I'm **PayPilot**, your AI checkout agent. Tell me what "
                "you're shopping for — e.g. *'wireless headphones under $100'* "
                "— and I'll find it, then check you out with PayPal.")

        if s["state"] == "await_pick":
            return self._handle_pick(s, text)

        if s["state"] == "await_confirm":
            return self._handle_confirm(s, low)

        if low == "done" and s.get("order_id"):
            return self._capture(s)

        if s["state"] == "await_approval":
            return self._say(
                "The PayPal approval page should be open in your browser. "
                "Approve the payment there, then type **done** and I'll "
                "capture it. (Sandbox mode — no real money moves.)")

        # default: treat as a shopping request
        return self._search_flow(s, text)

    # ---- flows ------------------------------------------------------------
    def _search_flow(self, s, text):
        budget = self._parse_budget(text)
        results = search(text, budget)
        if not results:
            return self._say(
                "I couldn't find a match. Try something like *'mechanical "
                "keyboard under $80'* or *'yoga mat'*.")
        s["shortlist"] = results[:3]
        s["state"] = "await_pick"
        lines = ["I found these for you:"]
        for i, p in enumerate(s["shortlist"], 1):
            lines.append(f"**{i}. {p['name']}** — ${p['price']:.2f} "
                         f"({p['category']})")
        lines.append("Reply with the **number** to pick one.")
        return self._say("\n".join(lines))

    def _handle_pick(self, s, text):
        m = re.search(r"\d+", text)
        idx = int(m.group()) - 1 if m else -1
        items = s.get("shortlist", [])
        if not (0 <= idx < len(items)):
            return self._say("Please reply with 1, 2 or 3.")
        s["pending"] = items[idx]
        s["state"] = "await_confirm"
        p = items[idx]
        return self._say(
            f"You picked **{p['name']}** (${p['price']:.2f}).\n"
            f"_{p['blurb']}_\n\n"
            f"Type **yes** and I'll create a PayPal order for it.")

    def _handle_confirm(self, s, low):
        if "yes" not in low and "ok" not in low:
            s["state"] = "idle"
            return self._say("No problem — cancelled. What else can I find?")
        p = s["pending"]
        order = self.paypal.create_order(
            p["price"], f"PayPilot: {p['name']}",
            f"{self.base_url}/success", f"{self.base_url}/cancel")
        s["order_id"] = order["id"]
        s["state"] = "await_approval"
        url = self.paypal.approval_url(order)
        mode_note = (" *(mock mode — add sandbox keys for the real PayPal "
                     "flow)*" if self.paypal.mode == "mock" else "")
        return {"text": (f"✅ PayPal order **{order['id']}** created for "
                         f"${p['price']:.2f}.{mode_note}\n\n"
                         f"👉 **[Approve on PayPal Sandbox]({url})**\n\n"
                         f"After approving, type **done**."),
                "order_id": order["id"], "approval_url": url,
                "paypal_mode": self.paypal.mode}

    def _capture(self, s):
        res = self.paypal.capture_order(s["order_id"])
        p = s.get("pending", {})
        s["state"] = "idle"
        s["order_id"] = None
        ok = res.get("status") == "COMPLETED"
        return self._say(
            ("🎉 **Payment captured!** " if ok else "⚠️ Capture returned: "
             f"{res.get('status')}. ")
            + (f"Order for **{p.get('name', 'your item')}** is complete. "
               f"Receipt: `{s.get('order_id') or res.get('id')}`."))

    # ---- helpers ------------------------------------------------------------
    @staticmethod
    def _say(text, **kw):
        d = {"text": text}
        d.update(kw)
        return d

    @staticmethod
    def _parse_budget(text):
        m = re.search(r"under\s*\$?(\d+(?:\.\d+)?)", text.lower())
        if m:
            return float(m.group(1))
        m = re.search(r"\$(\d+(?:\.\d+)?)", text)
        if m:
            return float(m.group(1)) * 1.5
        return None
