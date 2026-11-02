import json, os
import io
import warnings
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool
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
    "Looks OK": "We did not spot common scam signs, but this is not proof it is safe. If you were not expecting it, check with the sender another way.",
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
MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_TEXT_CHARS = 12000
MAX_IMAGE_PIXELS = 16_000_000
MAX_REQUEST_BYTES = 9 * 1024 * 1024

class BoundedUpload:
    """Reject oversized bodies before multipart parsing or disk spooling."""
    def __init__(self, application):
        self.application = application

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope['method'] != 'POST' or scope['path'] != '/api/check':
            return await self.application(scope, receive, send)
        headers = dict(scope.get('headers', []))
        try:
            length = int(headers.get(b'content-length', b'0'))
        except ValueError:
            return await JSONResponse({'detail': 'Invalid upload length.'}, status_code=400)(scope, receive, send)
        async def reject():
            await JSONResponse({'detail': 'Upload is too large. Choose a photo under 8 MiB and shorten the message.'},
                               status_code=413)(scope, receive, send)
        if length > MAX_REQUEST_BYTES:
            return await reject()
        chunks, total = [], 0
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            chunk = message.get('body', b'')
            total += len(chunk)
            if total > MAX_REQUEST_BYTES:
                return await reject()
            chunks.append(chunk)
            if not message.get('more_body', False):
                break
        body = b''.join(chunks)
        delivered = False
        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {'type': 'http.request', 'body': body, 'more_body': False}
            return await receive()
        await self.application(scope, replay, send)

app.add_middleware(BoundedUpload)
IMAGE_TYPES = {
    "image/png": lambda b: b.startswith(b"\x89PNG\r\n\x1a\n"),
    "image/jpeg": lambda b: b.startswith(b"\xff\xd8\xff"),
}

def validated_image(data, claimed_mime):
    """Bound upload size and verify actual format before sending bytes to a model."""
    if not data:
        raise HTTPException(status_code=400, detail="The picture is empty. Choose another photo.")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Picture is too large. Choose a PNG or JPEG under 8 MB.")
    mime = (claimed_mime or "").lower().strip()
    if mime == "image/jpg":
        mime = "image/jpeg"
    if mime not in IMAGE_TYPES or not IMAGE_TYPES[mime](data):
        raise HTTPException(status_code=415, detail="Use a valid PNG or JPEG picture.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as picture:
                if picture.width * picture.height > MAX_IMAGE_PIXELS:
                    raise HTTPException(status_code=413, detail="Picture has too many pixels. Choose a smaller photo.")
                if picture.format != {'image/png': 'PNG', 'image/jpeg': 'JPEG'}[mime]:
                    raise ValueError('format mismatch')
                if getattr(picture, 'n_frames', 1) != 1:
                    raise ValueError('animated image')
                picture.verify()
            with Image.open(io.BytesIO(data)) as picture:
                picture.load()
    except (Image.DecompressionBombWarning, Image.DecompressionBombError):
        raise HTTPException(status_code=413, detail="Picture has too many pixels. Choose a smaller photo.") from None
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError):
        raise HTTPException(status_code=415, detail="This picture could not be opened. Choose a complete PNG or JPEG photo.") from None
    return mime

def merge_flags(ai_flags, hits):
    """Only reviewed warnings reach the UI, speech, and family sharing.

    AI prose is untrusted: a flag can itself contain payment instructions or
    falsely claim that a rule warning is safe. The AI verdict still contributes.
    """
    return [h['flag'] for h in sorted(hits, key=lambda h: -h['weight'])][:MAX_FLAGS]

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
    step = STEPS[v]  # Fixed, reviewed advice: do not allow untrusted text to supply an action.
    return v, flags, step

@app.post("/api/check")
async def check(text: str = Form(""), image: UploadFile | None = File(None)):
    if len(text) > MAX_TEXT_CHARS:
        raise HTTPException(status_code=413, detail="Message is too long. Please shorten it.")
    img = await image.read(MAX_IMAGE_BYTES + 1) if image else None
    mime = validated_image(img, image.content_type) if image else None
    if not text.strip() and not img:
        raise HTTPException(status_code=400, detail="Please paste a message or add a picture.")
    ai, source, err = None, "rules", None
    live = not demo_mode()
    if not live:
        source = "demo (rules only, no AI)"
        if not text.strip() and img:
            return {"verdict": "Be Careful", "flags": ["Demo mode can't read pictures. Add a Meta API key, or paste the words."],
                    "next_step": STEPS["Be Careful"], "source": source, "demo_mode": True, "help": HELP}
    else:
        try:
            ai = await run_in_threadpool(meta_client.analyze, text, img, mime, [h["flag"] for h in rules.precheck(text)["hits"]])
            source = f"Meta {meta_client.MODEL} + rules"
        except Exception:  # no raw exception details go back to the browser
            err, source = "AI analysis was unavailable; built-in checks were used.", "rules (AI call failed)"
    extracted = (ai.get("extracted_text") or "") if ai else ""
    # Check BOTH the pasted message and words read from a photo.
    rule = rules.precheck("\n".join(part for part in (text, extracted) if part))
    v, flags, step = combine(rule, ai)
    if img and (not extracted.strip() or not ai or ai.get('image_readable') is not True):
        # Even a confident-looking verdict cannot verify an unreadable photo.
        if v == "Looks OK":
            v, step = "Be Careful", STEPS["Be Careful"]
        flags = flags + ["We could not confirm all the words in this picture. Try a clearer photo or paste the words."]
        flags = flags[:MAX_FLAGS]
    if err and v == "Looks OK":
        v, step = "Be Careful", STEPS["Be Careful"]
        flags = ["The AI checker was unavailable. We cannot confirm that this message is safe."] + flags
    if not flags:
        flags = ["We didn't find common scam signs. This does not prove it is safe."] if v == "Looks OK" else ["The AI found possible warning signs. Check with someone you trust before acting."]
    return {"verdict": v, "flags": flags[:MAX_FLAGS], "next_step": step, "source": source, "demo_mode": not live,
            "rule_score": rule["score"], "ai_error": err, "help": HELP}

app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
