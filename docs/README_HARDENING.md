# Is This a Scam? — photo/upload safety patch (November 2, 2026)

Status: LOCAL REVIEW CANDIDATE ONLY — NOT pushed to GitHub, not deployed, not independently accepted.
Source: public GitHub repository whyitworks307/is-this-a-scam, main commit
`0fff8aff37b256e5360438e45a03cb9e6b53c846`.

## Contents
- `scam_hardening_review_patch.diff` — the exact three-file patch for app.py, meta_client.py and static/index.html.
- `tests/test_hardening.py` — 29 no-network/no-credit pytest checks.
- `docs/README_HARDENING.md` — this guide.

## Intended improvement
- Photo of a paper letter is supported through the existing upload pathway (not a new AI model).
- Only PNG/JPEG uploads, magic-byte format checks, max 8 MiB; max 12,000 message characters.
- Rule engine checks BOTH typed text and extracted photo text.
- Incomplete/unreadable photos never produce an unqualified "Looks OK" result.
- AI failures never disclose raw exception details or claim normal messages are verified safe.
- Deterministic serious warnings cannot be crowded out by AI-generated flags.
- Static reviewed safe next steps replace arbitrary AI-generated action instructions.
- UI explains photo privacy/format, shows API errors and always unlocks the button.

## Apply safely on a copy/branch
This is not a complete standalone application. Keep the current submitted/demo version intact.

1. On the computer with the repository, confirm `git status` is clean and `git rev-parse HEAD` is the source commit above.
2. Run `git switch -c photo-hardening-review-20261102`.
3. In the repo root, run `git apply --check /path/to/scam_hardening_review_patch.diff`.
4. Run `git apply /path/to/scam_hardening_review_patch.diff`.
5. Copy `tests/test_hardening.py` to the repo's `tests/test_hardening.py`.
6. Run `python -m pytest -q tests/test_hardening.py` after installing the repo's requirements plus pytest/httpx if needed.
7. Start the app with the existing `META_API_KEY` set locally, *never print or commit it*. Validate three clear photos, two blurry/poorly lit photos, and a normal non-scam message against the API. Each live call consumes credits.
8. Have the independent reviewer check the live results and record failures. Merge only if accepted, and only if safe before deadline.

Do not copy any API keys into ChatGPT, this ZIP, screenshots or GitHub. No credits were spent making this patch. No live Meta API calls were performed in this environment.

Limits: Static-image format checks do not guarantee content readability. User must still verify critical financial claims through trusted channels. This patch does not implement PDF reading or independent fact verification.
