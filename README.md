# Is This a Scam? — a scam checker for older adults

Paste a suspicious text, email, or DM (or upload a screenshot). The app gives a big verdict
(**Likely Scam / Be Careful / Looks OK**), red flags in plain words, one safe next step, and the
AARP Fraud Watch Network Helpline (877-908-3360, Mon–Fri 8am–8pm ET, checked at
https://www.aarp.org/money/scams-fraud/helpline/ on Oct 30 2026).

## Photo hardening candidate — November 2, 2026

This branch is a review candidate. It has not been independently accepted or deployed.
The original working demo and submission files are preserved. See
[the release report](docs/HARDENING_REPORT.md) and [Vex handoff](docs/VEX_HANDOFF.md).

- Upload a clear, complete PNG/JPEG photo of a letter, invoice, notice, or message.
  Maximum: 8 MiB and 16 million pixels; text: 12,000 characters.
- Typed text and words extracted from the image both go through the existing rules.
- Invalid, incomplete, or unreadable input gets a clear error or cautious result.
- All displayed warnings and next steps use reviewed text. The AI contributes its
  verdict and image transcription; arbitrary AI advice is never displayed or read aloud.
- **Looks OK means common warning signs were not spotted. It does not verify the sender,
  payment request, or document.** Even a confident model can misread a photograph.
- Live mode sends the supplied message/photo to Meta. Cover private information first.
  This app has no document database; Meta's service policies still apply.

Run offline regression tests with `python -m pip install -r requirements-test-lock.txt`
then `python -m pytest`. The original server test remains `python test_samples.py`.
The lock records the tested Linux environment; production dependencies remain in
`requirements.txt`. Python 3.10+ is required. Builder tests passed on Windows too;
independent Vex QC is still pending.

The optional live campaign is separate from normal app use. Read
[the live test instructions](docs/LIVE_TESTING.md) before running it. It requires
verified promotional-only billing and an existing local `META_API_KEY`; it does
not configure payment methods or verify your credit balance itself.

## Setup
```bash
cd scam_checker
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run in demo mode (no key needed)
```bash
DEMO_MODE=1 uvicorn app:app --port 8000
```
Open http://127.0.0.1:8000. A yellow "DEMO MODE" banner shows. Demo mode uses only the rules
(it can't read screenshots). Tip: `http://127.0.0.1:8000/?sample=irs` auto-runs a sample.

## Add your Meta API key
Get a key at https://dev.meta.ai, then (never put the key in code or git):
```bash
export META_API_KEY="your-key"
export META_API_BASE="https://api.meta.ai/v1"   # default
export META_MODEL="muse-spark-1.3"              # default
uvicorn app:app --port 8000
```
If `META_API_KEY` is empty, the app falls back to demo mode automatically.

## Test
With the server running: `python test_samples.py` (checks all 12 samples).

## Architecture
```
static/index.html  -> one page: big text, one "Check It" button, read-aloud (speechSynthesis),
                      "Send to my family" (sms: on phones, mailto: on computers)
app.py (FastAPI)   -> POST /api/check
   1. rules.py      deterministic pre-check: urgency, gift cards, wire/crypto, secrecy,
                    odd links, personal info, threats, prizes, family emergency, tech support,
                    romance, too-good-to-be-true. Weighted score -> verdict.
   2. meta_client.py  Meta Model API (Muse Spark, OpenAI-compatible /chat/completions).
                    Sends text and/or screenshot + the rule hits; asks for JSON
                    {verdict, flags, next_step, extracted_text}.
   3. combine()     safety-first merge: the more cautious verdict wins; a strong rule hit
                    can never be downgraded to "Looks OK"; flags are merged.
   If the AI call fails, the app still answers using the rules.
samples.json       -> 10 scams + 2 real messages for the demo.
```

## Prior baseline live-mode evidence (reported Oct 31 2026)
- Run live: `env -u DEMO_MODE .venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000` with `META_API_KEY` set in the environment (use the `.venv`; system Python has no uvicorn).
- `POST https://api.meta.ai/v1/chat/completions`, model `muse-spark-1.3`, OpenAI-style body, `reasoning_effort: "low"` works as written. No `response_format` needed: the prompt-asked JSON parses cleanly.
- Screenshot input works on chat completions using an OpenAI-style `image_url` part with a `data:image/png;base64,...` URL. The model returns the text it reads in `extracted_text`. The Responses API isn't needed.
- `python3 test_samples.py` in live mode: 12/12 pass (10 scams are Likely Scam, 2 real messages are Looks OK). Takes about 3 s per call.
- The DEMO MODE banner is hidden when a key is set. Live screenshot: `screenshot_live.png` (sample image: `sample_scam_screenshot.png`).
- AI flags and rule flags are merged so the same warning isn't listed twice.
- If a screenshot can't be read (AI down or error), the app says "Be Careful" and asks you to paste the words. It never says "Looks OK" for a picture it couldn't read.
