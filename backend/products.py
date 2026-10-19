"""Demo product catalog for the PayPilot store."""
CATALOG = [
    {"id": "p1", "name": "Aria Wireless Headphones",
     "price": 89.99, "category": "audio",
     "blurb": "Noise-cancelling over-ears, 40h battery.",
     "tags": ["headphones", "wireless", "audio", "music", "bluetooth"]},
    {"id": "p2", "name": "Pulse True-Wireless Earbuds",
     "price": 49.99, "category": "audio",
     "blurb": "Compact buds with charging case, 24h total.",
     "tags": ["earbuds", "wireless", "audio", "music", "bluetooth"]},
    {"id": "p3", "name": "Forge Mechanical Keyboard",
     "price": 79.00, "category": "computing",
     "blurb": "Hot-swap RGB keyboard, tactile switches.",
     "tags": ["keyboard", "mechanical", "computing", "typing", "rgb"]},
    {"id": "p4", "name": "Stratus Yoga Mat Pro",
     "price": 35.50, "category": "fitness",
     "blurb": "6mm non-slip mat with alignment lines.",
     "tags": ["yoga", "mat", "fitness", "exercise"]},
    {"id": "p5", "name": "Lumen Desk Lamp",
     "price": 42.00, "category": "home",
     "blurb": "Eye-care LED lamp, 5 color temperatures.",
     "tags": ["lamp", "desk", "light", "home", "office"]},
    {"id": "p6", "name": "Voyager Backpack 25L",
     "price": 65.00, "category": "travel",
     "blurb": "Water-resistant, laptop sleeve, USB passthrough.",
     "tags": ["backpack", "travel", "bag", "laptop"]},
    {"id": "p7", "name": "Tempo Smart Speaker",
     "price": 99.00, "category": "audio",
     "blurb": "Room-filling sound with voice assistant.",
     "tags": ["speaker", "smart", "audio", "music", "voice"]},
    {"id": "p8", "name": "Aero Running Shoes",
     "price": 120.00, "category": "fitness",
     "blurb": "Lightweight knit runners, responsive foam.",
     "tags": ["shoes", "running", "fitness", "sneakers"]},
]


def search(query, budget=None):
    """Score catalog items against a natural-language query."""
    words = {w for w in query.lower().split() if len(w) > 2}
    scored = []
    for p in CATALOG:
        hay = " ".join([p["name"], p["category"], p["blurb"],
                        " ".join(p["tags"])]).lower()
        hits = sum(1 for w in words if w in hay)
        if hits == 0:
            continue
        if budget is not None and p["price"] > budget:
            continue
        scored.append((hits, -p["price"], p))
    scored.sort(reverse=True)
    return [p for _, _, p in scored]
