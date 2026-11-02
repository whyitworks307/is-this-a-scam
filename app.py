import re
import json, os
from pathlib import Path
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import rules, meta_client

ROOT = Path(__file__).parent
SAMPLES = json.loads((ROOT / "samples.json").read_text())
ORDER = {"Looks OK": 0, "Be Careful": 1, "Likely Scam": 2}
HELP = [
    {"name": "AARP Fraud Watch Network Helpline (free, Mon-Fri 8am-8pm ET)", "number": "877-908-3360",
     "source": "https://www.aarp.org/money/scams-fraud/helpline/"},
]
STEPS = {
    "Likely Scam": "Don't click. Don't pay. Don't reply. Call a family member, or call the company using the number on your card or bill.",
    "Be Careful": "Don't click any links yet. Call the company or person using a number you already know to check.",
    "Looks OK": "This looks normal. If anything feels wrong, ask a family member before you act.",
}

def demo_mode():
    return os.environ.get("DEMO_MODE", "").lower() in ("1", "true", "yes") or not meta_client.api_key()

app = FastAPI()

@app.get("/")
def index():
    return FileResponse(ROOT / "static" / "index.html")

@app.get("/api/config")
def config():
    return {"demo_mode": demo_mode(), "model": meta_client.MODEL, "help": HELP}

@app.get("/api/samples")
def samples():
    return [{"id": s["id"], "label": s["label"], "text": s["text"]} for s in SAMPLES]

MAX_FLAGS = 4
# words that show a model flag already covers a rule category
RULE_KEYWORDS = {
    "urgency": ["rush", "urgent", "immediately", "hurry", "pressure", "right now", "deadline", "hours", "act now", "quickly", "fast", "expire", "suspend"],
    "gift_cards": ["gift card", "gift-card", "itunes", "google play", "steam card"],
    "wire_crypto": ["wire", "zelle", "crypto", "bitcoin", "western union", "moneygram", "cash app", "venmo", "cash"],
    "secrecy": ["secret", "don't tell", "do not tell", "not to tell", "keep it quiet", "between us", "hide"],
    "odd_link": ["link", "url", "website", "web address", "click", "tap"],
    "personal_info": ["social security", "ssn", "medicare", "bank", "account number", "password", "pin", "personal info", "private info", "identity"],
    "threat": ["arrest", "warrant", "lawsuit", "police", "jail", "fine", "penalt", "legal", "threat"],
    "prize": ["won", "prize", "winner", "lottery", "sweepstakes", "fee"],
    "family_emergency": ["grandson", "granddaughter", "grandchild", "family member", "bail", "accident", "hospital", "in trouble"],
    "remote_access": ["remote", "computer", "virus", "anydesk", "teamviewer", "tech support"],
    "romance_money": ["romance", "online", "love", "sweetheart", "plane ticket", "customs"],
    "too_good": ["guarantee", "risk-free", "no risk", "double", "too good", "return"],
}
_STOP = set("it the a an you your to of and or for in on is are be that this they them with by as at not no from".split())

def _words(t):
    return {w for w in re.findall(r"[a-z']+", t.lower()) if len(w) > 3 and w not in _STOP}

def _covers(ai_flag, hit):
    t = ai_flag.lower()
    if any(k in t for k in RULE_KEYWORDS.get(hit["id"], [])):
        return True
    a, r = _words(ai_flag), _words(hit["flag"])
    return bool(a and r) and len(a & r) / min(len(a), len(r)) >= 0.5

def merge_flags(ai_flags, hits):
    """Model flags first (more specific); add a rule flag only if no model flag covers it."""
    out = []
    for f in ai_flags:
        f = str(f).strip()
        if f and f.lower() not in {x.lower() for x in out}:
            out.append(f)
    for h in sorted(hits, key=lambda h: -h["weight"]):
        if not any(_covers(f, h) for f in out):
            out.append(h["flag"])
    # keep strongest: model flags, then uncovered rule flags, cap at MAX_FLAGS
    return out[:MAX_FLAGS]

def combine(rule, ai):
    """Safety-first merge: take the more cautious verdict; merge flags."""
    if not ai:
        v = rule["verdict"]
        return v, [h["flag"] for h in sorted(rule["hits"], key=lambda h: -h["weight"])][:MAX_FLAGS], STEPS[v]
    av = ai.get("verdict") if ai.get("verdict") in ORDER else "Be Careful"
    v = max(rule["verdict"], av, key=ORDER.get)
    # strong rule hit (gift cards, secrecy, wire/crypto) can't be overruled to "Looks OK"
    if rule["score"] >= 4 and v == "Looks OK":
        v = "Be Careful"
    flags = merge_flags(ai.get("flags") or [], rule["hits"])
    step = ai.get("next_step") if v == av and ai.get("next_step") else STEPS[v]
    return v, flags, step

@app.post("/api/check")
async def check(text: str = Form(""), image: UploadFile | None = File(None)):
    img = await image.read() if image else None
    mime = (image.content_type if image else None) or "image/png"
    ai, source, err = None, "rules", None
    if demo_mode():
        source = "demo (rules only, no AI)"
        if not text.strip() and img:
            return {"verdict": "Be Careful", "flags": ["Demo mode can't read pictures. Add a Meta API key, or paste the words."],
                    "next_step": STEPS["Be Careful"], "source": source, "demo_mode": True, "help": HELP}
    else:
        try:
            ai = meta_client.analyze(text, img, mime, [h["flag"] for h in rules.precheck(text)["hits"]])
            source = f"Meta {meta_client.MODEL} + rules"
            if not text.strip():
                text = ai.get("extracted_text", "")
        except Exception as e:  # fall back safely to rules
            err, source = str(e)[:200], "rules (AI call failed)"
    rule = rules.precheck(text)
    v, flags, step = combine(rule, ai)
    if img and not text.strip() and not ai:
        # we could not read the picture, so never say "Looks OK"
        v, flags, step = "Be Careful", ["We couldn't read this picture. Please type or paste the words."], STEPS["Be Careful"]
    if not flags:
        flags = ["We didn't find common scam signs."] if v == "Looks OK" else ["Something here looks unusual."]
    return {"verdict": v, "flags": flags, "next_step": step, "source": source, "demo_mode": demo_mode(),
            "rule_score": rule["score"], "ai_error": err, "help": HELP}

app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
