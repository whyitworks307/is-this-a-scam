"""Deterministic rule-based pre-check. Runs with or without the AI model."""
import re
import unicodedata

_LEET = str.maketrans({'0':'o','1':'i','3':'e','4':'a','5':'s','7':'t'})
_SCAM_WORDS = {'gift','card','cards','bitcoin','crypto','wire','password','pin','ssn',
               'urgent','arrest','bail','grandson','granddaughter'}

def normalized_text(text: str) -> str:
    """Normalize rule matching only; never change the user's message or digits.

    Fold hidden formatting, full-width letters and a small set of obfuscated
    warning words. Pure numbers and unrelated alphanumeric identifiers stay intact.
    This is bounded evasion resistance, not a universal deobfuscation claim.
    """
    value=unicodedata.normalize('NFKC',text or '').casefold()
    value=''.join(c for c in value if unicodedata.category(c)!='Cf')
    value=value.translate(str.maketrans({'\u2018':"'",'\u2019':"'",'\u2010':'-','\u2011':'-'}))
    def fold(match):
        token=match.group()
        if any(c.isalpha() for c in token) and any(c.isdigit() for c in token):
            candidate=token.translate(_LEET)
            if candidate in _SCAM_WORDS:
                return candidate
        return token
    return re.sub(r'\b[a-z0-9]+\b',fold,value)

# (id, plain-words flag, weight, regex patterns)
RULES = [
    ("urgency", "It rushes you. Scammers want you to act before you think.", 2,
     [r"\burgent\b", r"\bimmediately\b", r"\bright now\b", r"\bwithin (24|48) hours\b", r"\btoday only\b",
      r"\bact now\b", r"\bfinal (notice|warning)\b", r"\bexpires?\b", r"\bsuspended\b", r"\bavoid (arrest|penalt)"]),
    ("gift_cards", "It asks for gift cards. Real companies and the government never take gift cards as payment.", 4,
     [r"\bgift[\s-]*cards?\b", r"\bitunes\b", r"google play card", r"\bsteam card", r"target card", r"apple card numbers?"]),
    ("wire_crypto", "It asks you to send money by wire, Zelle, cash, or crypto. That money is very hard to get back.", 4,
     [r"\bwire\b", r"western union", r"moneygram", r"\bzelle\b", r"\bbitcoin\b", r"\bcrypto", r"\busdt\b",
      r"bitcoin atm", r"\bcash app\b", r"\bvenmo\b", r"send (the )?cash"]),
    ("secrecy", "It tells you to keep it secret. Scammers don't want your family to stop you.", 4,
     [r"don'?t tell", r"do not tell", r"keep (this|it) (a )?secret", r"between us", r"don'?t (call|talk to) (anyone|your)"]),
    ("odd_link", "It has a strange web link. Don't tap links in messages you didn't expect.", 3,
     [r"https?://\S*(\.xyz|\.top|\.info|\.click|\.live|\.cc|\.ru|bit\.ly|tinyurl)", r"https?://\d+\.\d+\.\d+\.\d+",
      r"https?://\S*-(secure|verify|login|support|update)\S*", r"https?://\S*(usps|amazon|paypal|medicare|irs|chase|wellsfargo)\S*\.(?!com\b|gov\b)\w+"]),
    ("personal_info", "It asks for private information like your Social Security, Medicare, or bank number.", 3,
     [r"social security( number)?", r"\bssn\b", r"medicare (number|card)", r"account number", r"\bpin\b",
      r"verify your (identity|account)", r"password", r"routing number"]),
    ("threat", "It threatens you with arrest, fines, or losing your account.", 3,
     [r"\barrest", r"\bwarrant\b", r"\blawsuit\b", r"\bpolice\b", r"\bdeport", r"\bpenalt(y|ies)\b", r"legal action"]),
    ("prize", "It says you won something you never entered. You never have to pay to get a real prize.", 3,
     [r"you('ve| have)? won", r"\bwinner\b", r"\blottery\b", r"\bsweepstakes\b", r"claim your (prize|reward)", r"processing fee"]),
    ("family_emergency", "Someone says a family member is in trouble and needs money fast. Call that person yourself first.", 3,
     [r"\bgrandma\b", r"\bgrandpa\b", r"\bbail\b", r"\bin jail\b", r"\bhospital\b.*\bmoney\b", r"\baccident\b",
      r"(?s)\b(?:grandson|granddaughter|grandchild)\b.{0,140}\b(?:i need|send|pay|transfer)\b.{0,120}\b(?:money|dollars|lawyer|bail)\b"]),
    ("remote_access", "It wants you to call a number or let someone into your computer. Real tech companies don't do that.", 3,
     [r"virus", r"anydesk", r"teamviewer", r"remote access", r"call (microsoft|apple) support", r"your computer (is|has been)"]),
    ("romance_money", "Someone you only know online is asking for money. That is a very common scam.", 3,
     [r"my (love|darling|dear)", r"\bsweetheart\b", r"plane ticket", r"customs fee", r"stuck (overseas|abroad)"]),
    ("too_good", "It promises big money with no risk. That is too good to be true.", 3,
     [r"guaranteed (return|profit)", r"double your money", r"\brisk[- ]free\b", r"\d{2,}% (return|profit)"]),
]

def precheck(text: str) -> dict:
    t = normalized_text(text)
    hits, score = [], 0
    for rid, flag, w, pats in RULES:
        if any(re.search(p, t) for p in pats):
            hits.append({"id": rid, "flag": flag, "weight": w})
            score += w
    if score >= 5:
        verdict = "Likely Scam"
    elif score >= 2:
        verdict = "Be Careful"
    else:
        verdict = "Looks OK"
    return {"verdict": verdict, "score": score, "hits": hits}
