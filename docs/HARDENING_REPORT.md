# Photo hardening engineering report — November 2, 2026

Release recommendation: HOLD this branch for Vex independent QC. The capped live
campaign is now complete and passed; independent acceptance remains outstanding.
Do not merge or deploy it yet. Keep the existing working baseline available for
the November 4, 2026, 8:00 PM Central submission deadline.

## Patch provenance and application

- Repository: `whyitworks307/is-this-a-scam`.
- Starting/main commit: `0fff8aff37b256e5360438e45a03cb9e6b53c846`.
- Main matched that exact commit when recovered; local clone began clean.
- Isolated branch: `photo-hardening-review-20261102`.
- Review ZIP: 8844 bytes; SHA-256
  `bccd422f884e76e27c717cb7d86a36806cd4375ede4d5cde38bc158ebbce1ad8`.
- Drive and Library copies had identical hashes. ZIP CRC and member paths checked.
- Three expected members present. Instructions read; `git apply --check` and
  `git apply` succeeded without conflict against the expected source.
- Supplied checks first reproduced: 29/29. This was builder evidence only.

## Demonstrated gaps and repairs

Six additional checks failed against the recovered patch. See
`evidence/defects_before.txt` for the actual failures. All pass after repair:

| Gap | Repair |
| --- | --- |
| PNG signature followed by junk accepted | Full format verification and pixel decoding |
| JPEG signature followed by junk accepted | Same, including actual format/MIME match |
| False reassuring AI flag hides gift-card warning | Deterministic warnings sorted by weight; no AI-prose suppression |
| AI flag tells user to pay an attacker | Reviewed flags and next steps only, including speech and family draft |
| Partly read image marked Looks OK | Explicit readability signal required; missing/false is cautious |
| Small compressed image expands to 25 million pixels | 16-million-pixel limit before decode |

Further bounded repairs: total HTTP body capped before multipart parsing (including
chunked uploads); 64 KiB Meta reply cap; 4096 output token limit; explicit complete
response required; API redirects and nonofficial/insecure endpoints rejected; raw
exceptions hidden; synchronous model call moved off the async event loop. No retry
was added. UI adds inline announced errors, progress/disabled controls, timeout
recovery, keyboard focus, photo privacy help, and sample-photo reset.

The original 29-check suite remains represented. Its fake-header PNG/JPEG fixtures
were replaced with real decodable images; its unreadable-photo assertion now checks
the warning list rather than requiring that warning to displace serious rule hits.
The exact unmodified supplied tests remain recoverable in the pinned review ZIP.

## Test evidence

- 101/101 offline pytest cases: `evidence/regression.txt` and `regression.xml`.
  The same 101 tests passed on the laptop under Windows/Python 3.13.
- Original, unchanged server sample runner: 12/12 in demo/rules mode,
  `evidence/original_samples.txt`. These overlap sample coverage in pytest; do not
  add the counts together as unique cases.
- Browser evidence: `evidence/browser_smoke.json`; headless Chromium, demo mode,
  external requests blocked. Browser smoke runner is separate from pytest.
- `compileall` and `git diff --check` passed.
- Dependency versions: `requirements-test-lock.txt`. One upstream TestClient/httpx
  deprecation warning is recorded; tests still pass.
- Live campaign: 13/13 expected verdicts, `evidence/live_meta_campaign.json`.
  Three clear synthetic document photos were Likely Scam. The blurred photo was
  Be Careful; the dark photo was Likely Scam. The benign text was Looks OK with
  the explicit safety caveat. All seven other scam/adversarial texts were Likely Scam.
- Usage estimate at uncached Standard rates: $0.050824, within the $5 cap. This is
  a token-derived estimate, not an observed invoice debit. Funding evidence is the
  account owner's explicit current confirmation of $149 free promotional credit.
  The API key was found only in the laptop's User environment and stayed there.
  The official free model-catalog call authenticated successfully. A signed-in
  billing dashboard was not available; no claim is made that personal billing
  settings were disabled or changed. No purchase or payment configuration was made.
- Thirteen live cases establish only this small synthetic campaign's outcome.
  Genuine camera-photo accuracy and a general false-positive/false-negative rate
  remain unmeasured. API failure scenarios were simulated offline, not induced
  through paid calls.

## Security and remaining limits

No actual key was printed, exported from the laptop, or committed. Offline tests block
external HTTP and use an obviously fake key. No changes to Personal Relay occurred.
No production deployment, main merge, or submission occurred. Existing video,
voiceover, demo script, submission draft, and sample media are preserved.

Model transcription and readability are still model judgments. A confidently wrong
transcription can miss a warning; a malicious document may still manipulate a model
verdict when deterministic words are absent. Fixed advice prevents arbitrary model
actions, not all false negatives. Rules use keywords and can warn on benign mentions
of scam-related terms. No independent sender, URL, legal, or financial verification
is performed. No PDFs, HEIC, animated images, or handwriting guarantee were added.
Server concurrency/global spending limits and public hosting abuse protection are
outside this local candidate; do not expose a live-key server publicly without review.

Vex decision: PENDING. Builder success is not independent acceptance. No reachable
Vex execution channel was identified; the handoff is prepared, not represented as
a completed review or confirmed delivery.
