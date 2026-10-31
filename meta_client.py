"""Calls the Meta Model API (Muse Spark).

Docs checked Oct 30 2026: https://dev.meta.ai/docs/protocols/chat-completions
- POST {META_API_BASE}/chat/completions, header "Authorization: Bearer <key>"
- OpenAI-compatible body: {"model": "muse-spark-1.3", "messages": [...]}
- Muse Spark accepts image input. The image message shape below uses the
  OpenAI-style "image_url" content part (base64 data URL). VERIFIED live Oct 31 2026.
- Structured output is listed as supported; we ask for JSON in the prompt
  AND parse defensively, so it works even if response_format differs.
Edit EVERYTHING in the "EDIT HERE" block if the API changes.
"""
import base64, json, os, re
import requests

# ===== EDIT HERE =====
API_BASE = os.environ.get("META_API_BASE", "https://api.meta.ai/v1")
MODEL = os.environ.get("META_MODEL", "muse-spark-1.3")
TIMEOUT = 60
# =====================

SYSTEM_PROMPT = """You help older adults decide if a message is a scam.
Read the message (text or screenshot). Answer ONLY with JSON, no other text:
{"verdict": "Likely Scam" | "Be Careful" | "Looks OK",
 "flags": ["short plain sentence", ...],
 "next_step": "one short safe action",
 "extracted_text": "the text you read from the screenshot, or empty"}
Rules: write at a 6th-grade reading level. Short sentences. No jargon.
At most 5 flags. Be honest: if it looks like a normal message, say "Looks OK".
A rule-based checker already found these warning signs (may be empty or wrong):
"""

def api_key():
    return os.environ.get("META_API_KEY", "").strip()

def _parse_json(s: str) -> dict:
    m = re.search(r"\{.*\}", s, re.S)
    if not m:
        raise ValueError("model did not return JSON")
    return json.loads(m.group(0))

def analyze(text: str, image_bytes: bytes | None, image_mime: str, rule_flags: list[str]) -> dict:
    content = [{"type": "text", "text": "Message to check:\n" + (text or "(see screenshot)")}]
    if image_bytes:
        b64 = base64.b64encode(image_bytes).decode()
        content.append({"type": "image_url", "image_url": {"url": f"data:{image_mime};base64,{b64}"}})  # verified working Oct 31 2026
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT + json.dumps(rule_flags)},
            {"role": "user", "content": content},
        ],
        "reasoning_effort": "low",  # Muse Spark rejects "none"
    }
    r = requests.post(f"{API_BASE}/chat/completions",
                      headers={"Authorization": f"Bearer {api_key()}", "Content-Type": "application/json"},
                      json=body, timeout=TIMEOUT)
    r.raise_for_status()
    msg = r.json()["choices"][0]["message"]["content"]
    if isinstance(msg, list):
        msg = "".join(p.get("text", "") for p in msg)
    return _parse_json(msg)
