# Vex independent QC handoff

Project: Is This a Scam? Photo hardening candidate, November 2, 2026.
Decision required from Vex: explicit ACCEPTED or REJECTED with independent evidence.
Current decision: PENDING — no Vex decision has been received.

Review branch `photo-hardening-review-20261102` in
https://github.com/whyitworks307/is-this-a-scam . Compare with starting commit
`0fff8aff37b256e5360438e45a03cb9e6b53c846`. Use the exact PR head commit and record
it in your decision. Do not review a moving main checkout or edit this candidate
in place. Any repair creates a new candidate requiring review again.

1. Read `docs/HARDENING_REPORT.md`, `docs/LIVE_TESTING.md`, and the original review ZIP.
2. Create a clean environment. Install `requirements-test-lock.txt`; run
   `python -m pytest` and the unchanged `test_samples.py` against a demo-mode server.
3. Independently challenge uploads: MIME mismatch, empty/truncated/corrupt images,
   8 MiB boundary, pixel bombs, animation, body limit, chunked input, and text limits.
4. Exercise model timeout, 402/429/5xx, malformed/oversize JSON, incomplete output,
   missing/false readability, malicious flags/actions, and suppression of serious rules.
5. Verify both typed and extracted words are checked. Do not treat Looks OK as
   independently verified legitimacy. Include benign and adversarial cases.
6. Inspect key handling and official endpoint enforcement. Never print any real key.
7. Independently inspect mobile layout, keyboard navigation, readable errors, speech
   text, and family-share draft. Do not actually message a third party during QC.
   A Chromium smoke runner is in `tools/browser_smoke.py` (requires Playwright).
8. Independently inspect the completed 13-case live report and its token-derived
   $0.050824 use estimate. Funding evidence was the owner's current $149 free-credit
   confirmation; it was not a dashboard audit. If you rerun any paid tests, first
   verify remaining promotional funding and allocate the remaining campaign budget.
   Do not reset the ledger or silently reuse the baseline's separate live results.
9. Report incorrect verdicts, false confidence, missed/extra warnings, usability limits,
   exact commands/environment, request usage, and reproducibility. Keep raw secrets out.

Do not merge/deploy or make submission claims. If evidence is insufficient, reject
or explicitly scope the decision to offline engineering and list the remaining gate.
The deadline is November 4, 2026, 8:00 PM Central. The working baseline remains the
submission fallback if this candidate has not passed independent QC in time.
