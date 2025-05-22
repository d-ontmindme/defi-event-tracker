#!/usr/bin/env python3
"""
snapshot_alert.py  •  Minimal watcher for Snapshot governance proposals
────────────────────────────────────────────────────────────────────────
• Polls chosen Snapshot “spaces” every 90 s
• Classifies proposals (Low | Mid | High) via keyword rules
• Detects probable price-moving proposals (‘burn’, ‘mint’, ‘buyback’ …)
• SMS / WhatsApp alert through Twilio
"""

import os, json, time, requests, pathlib, textwrap, logging, sys
from datetime import datetime as dt
from dotenv import load_dotenv
from twilio.rest import Client

# ──────────────────────────────────── config ───────────────────────────────────
POLL_INTERVAL = 90                              # seconds
SPACES        = ["uniswap", "aave.eth"]         # Snapshot “space” strings

KEYWORDS_HIGH = {
    "hack", "security exploit", "emergency",
    "burn", "mint", "buyback", "supply", "token supply",
    "inflation", "deflation", "dividend", "yield",
    "revenue", "allocation"
}
KEYWORDS_MID  = {
    "fee", "treasury", "reward", "liquidity", "emission",
    "parameter", "governance", "upgrade"
}
PRICE_IMPACT  = { "burn", "mint", "buyback", "supply",
                  "inflation", "deflation" }

load_dotenv()                                   # read .env
TWILIO_SID   = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM  = os.getenv("TWILIO_FROM")         # e.g. whatsapp:+14155238886
ALERT_TO     = os.getenv("ALERT_TO")            # e.g. whatsapp:+15551234567
if not all([TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM, ALERT_TO]):
    sys.exit("❌  Twilio environment variables missing; aborting.")

# ────────────────── helpers ──────────────────
ROOT        = pathlib.Path(__file__).parent
SEEN_FILE   = ROOT / "seen.json"
SEEN        = json.loads(SEEN_FILE.read_text()) if SEEN_FILE.exists() else set()
if isinstance(SEEN, list): SEEN = set(SEEN)      # back-compat

client = Client(TWILIO_SID, TWILIO_TOKEN)
logging.basicConfig(format="%(asctime)s  %(levelname)s  %(message)s",
                    level=logging.INFO, datefmt="%H:%M:%S")

GQL_URL = "https://hub.snapshot.org/graphql"
QUERY = textwrap.dedent("""
query Recent($space:String!,$n:Int!){
  proposals(space:$space, first:$n, orderBy:"created", orderDirection:desc){
    id title body created choices state
  }
}
""")

def fetch_latest(space: str, n: int = 10):
    """Return list of newest proposals (dicts) for a Snapshot space."""
    resp = requests.post(GQL_URL, json={"query": QUERY,
                                        "variables": {"space": space, "n": n}},
                         timeout=15)
    resp.raise_for_status()
    return resp.json()["data"]["proposals"]

def classify(text: str):
    """Return (priority, price_impact_flag)."""
    low = text.lower()
    if any(k in low for k in KEYWORDS_HIGH):
        return "HIGH", any(k in low for k in PRICE_IMPACT)
    if any(k in low for k in KEYWORDS_MID):
        return "MID",  False
    return "LOW", False

def alert(proposal, priority: str, price_impact: bool):
    url   = f"https://snapshot.org/#/{proposal['id']}"
    tag   = "⚠️" if priority=="HIGH" else "ℹ️"
    pi    = "🚀 Price-moving!" if price_impact else ""
    body  = f"{tag} [{priority}] {proposal['title']}\n{pi}\n{url}"
    try:
        msg = client.messages.create(to=ALERT_TO, from_=TWILIO_FROM, body=body)
        logging.info("Sent alert %s  sid=%s", proposal['id'], msg.sid)
    except Exception as e:
        logging.error("Twilio error: %s", e)

def save_seen():
    SEEN_FILE.write_text(json.dumps(sorted(SEEN)))

# ────────────────── main loop ────────────────────
logging.info("Watcher started. Spaces: %s", ", ".join(SPACES))
try:
    while True:
        for space in SPACES:
            try:
                for p in fetch_latest(space):
                    if p["id"] in SEEN: break   # already looked at newer ones
                    priority, impact = classify(p["title"] + " " + p["body"])
                    alert(p, priority, impact)
                    SEEN.add(p["id"])
            except Exception as e:
                logging.warning("Fetch failed for %s : %s", space, e)
        save_seen()
        time.sleep(POLL_INTERVAL)
except KeyboardInterrupt:
    logging.info("Exiting.")
    save_seen()
