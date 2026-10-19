"""PayPal Sandbox REST client (Orders API v2) with transparent MOCK mode.

MOCK mode activates automatically when PAYPAL_CLIENT_ID / PAYPAL_CLIENT_SECRET
are not set, so the full checkout flow is demoable without credentials.
Swap to real sandbox by exporting the two env vars — no code change.
"""
import base64
import json
import os
import urllib.request
import uuid

# Secure credentials file (0600, outside any git repo).
# Created from the user's uploaded JSON; never committed, never logged.
CRED_FILE = os.path.expanduser(
    "~/workspace/custom-connectors/custom.paypal-sandbox/bin/.credentials.json")


def _load_file_creds():
    try:
        with open(CRED_FILE) as f:
            d = json.load(f)
        cid, sec = d.get("client_id"), d.get("client_secret")
        if cid and sec:
            return cid, sec
    except (OSError, ValueError):
        pass
    return None, None


class PayPalClient:
    def __init__(self, client_id=None, client_secret=None, sandbox=True):
        # Priority: explicit args > env vars > secure file > mock mode.
        if not client_id:
            client_id = os.environ.get("PAYPAL_CLIENT_ID")
        if not client_secret:
            client_secret = os.environ.get("PAYPAL_CLIENT_SECRET")
        if not (client_id and client_secret):
            fcid, fsec = _load_file_creds()
            client_id = client_id or fcid
            client_secret = client_secret or fsec
        self.client_id = client_id
        self.client_secret = client_secret
        self.base = ("https://api-m.sandbox.paypal.com" if sandbox
                     else "https://api-m.paypal.com")
        self.mode = "live" if (client_id and client_secret) else "mock"
        self._token = None

    # ---- auth ----------------------------------------------------------
    def _auth_token(self):
        if self.mode == "mock":
            return "mock-token"
        if self._token:
            return self._token
        creds = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()).decode()
        req = urllib.request.Request(
            f"{self.base}/v1/oauth2/token",
            data=b"grant_type=client_credentials",
            headers={"Authorization": f"Basic {creds}",
                     "Content-Type": "application/x-www-form-urlencoded"},
            method="POST")
        with urllib.request.urlopen(req, timeout=20) as r:
            self._token = json.load(r)["access_token"]
        return self._token

    def _call(self, method, path, body=None):
        if self.mode == "mock":
            return self._mock(method, path, body)
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            f"{self.base}{path}", data=data, method=method,
            headers={"Authorization": f"Bearer {self._auth_token()}",
                     "Content-Type": "application/json",
                     "PayPal-Request-Id": str(uuid.uuid4())})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)

    # ---- orders ---------------------------------------------------------
    def create_order(self, amount_usd, description, return_url, cancel_url):
        return self._call("POST", "/v2/checkout/orders", {
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {"currency_code": "USD",
                           "value": f"{amount_usd:.2f}"},
                "description": description[:120],
            }],
            "application_context": {
                "return_url": return_url,
                "cancel_url": cancel_url,
                "brand_name": "PayPilot Demo Store",
                "user_action": "PAY_NOW",
            },
        })

    def capture_order(self, order_id):
        return self._call("POST",
                          f"/v2/checkout/orders/{order_id}/capture", {})

    def approval_url(self, order):
        for link in order.get("links", []):
            if link.get("rel") == "approve":
                return link["href"]
        return None

    # ---- mock ------------------------------------------------------------
    def _mock(self, method, path, body):
        oid = "MOCK-" + uuid.uuid4().hex[:8].upper()
        if path == "/v2/checkout/orders":
            amt = body["purchase_units"][0]["amount"]["value"]
            return {
                "id": oid, "status": "CREATED",
                "links": [
                    {"rel": "self",
                     "href": f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{oid}"},
                    {"rel": "approve",
                     "href": f"https://www.sandbox.paypal.com/checkoutnow?token={oid}"},
                ],
                "_mock": True, "_amount": amt,
            }
        if path.endswith("/capture"):
            return {"id": oid, "status": "COMPLETED",
                    "_mock": True,
                    "note": "Mock capture — connect sandbox keys for real flow"}
        return {"_mock": True}
