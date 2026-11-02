# Vex independent QC — "Is This a Scam?" photo-hardening candidate

Date: Monday, November 2, 2026, ~10:40 AM CST (America/Chicago)
Reviewer: Vex (independent of builder GPT-6.1)
Environment: Linux box (Debian, Python 3.13.5, venv from `requirements-test-lock.txt`,
Playwright Chromium headless). **These are Linux results only. No Windows run was made;
the builder's Windows 101/101 is an unverified builder claim.**

## Pins
| Item | Value | Verified |
|---|---|---|
| Candidate ZIP (Drive 1GcqmEWu8JmNoDK3Au0ow3aHR1cR3SzSN) SHA-256 | `7fa011855b3f3cd3d0f6180029719d4adb74f669b6bd73489d78a4f3d08119b7` | MATCH |
| Git bundle SHA-256 | `422ef2860a0bd415c97cb7576b7583b27a3b359009cf33b6d7428dccd0c55733` | `git bundle verify` OK, complete history |
| Bundle head `photo-hardening-review-20261102` | `87d659b59a8d4b0bf484e02e8d10105167aef4ea` | MATCH; also matches GitHub `git ls-remote` |
| Main / base | `0fff8aff37b256e5360438e45a03cb9e6b53c846` | MATCH on GitHub; ancestor of candidate (2 commits) |
| Packet docs vs. commit | VEX_HANDOFF, HARDENING_REPORT, LIVE_TESTING, SUBMISSION_READINESS, live_meta_campaign.json | byte-identical to committed copies |

Candidate ZIP was made read-only; all work used a clone/copy (`work/`, mutants in fresh copies).

## Diff vs main
34 files, +2084/−74: app.py, meta_client.py, static/index.html, README, docs, evidence,
tests, tools, fixtures. **Unchanged** (git diff, byte-level): demo_silent.mp4, screenshot.png,
screenshot_live.png, sample_scam_screenshot.png, keyframes/ (6 files), SUBMISSION_DRAFT.md,
DEMO_SCRIPT.md, VOICEOVER.md, samples.json, rules.py, test_samples.py.

## Results (each a distinct run; no repeated runs counted)
| Check | Result |
|---|---|
| Builder regression suite (`pytest`, HTTP blocked by conftest) | 101/101 pass |
| Original `test_samples.py` vs demo-mode uvicorn on 127.0.0.1 | 12/12 pass |
| `tools/browser_smoke.py` headless Chromium, non-localhost requests aborted | 15/15 pass |
| **Vex new adversarial suite** (`test_vex_adversarial.py`, 74 test cases) | 72 pass, 2 xfail (documented known false negatives, F1) , 0 fail |
| **Mutation testing** (18 mutants of safety checks) | 16 killed, 2 survived (both equivalent/redundant, F3) |
| Secret scan (full git history, packet docs) | 0 real keys; only `FAKE_TEST_VALUE_NOT_A_SECRET` and empty `.env.example` |
| Live report re-computation | 13/13 pass; tokens 13,755 in / 7,913 out → $0.050824 recomputed, matches |

No Muse/Meta API calls and no network calls to model APIs were made. All model behavior was faked
(`meta_client.analyze` or `requests.post` monkeypatched; real `Session.request` blocked).
Network was used only for pip/Playwright install and `git ls-remote` to GitHub.

Vex suite coverage: truncated PNG/JPEG, random bytes after magic, MIME mismatch, GIF, SVG, empty,
PNG header pixel bomb (50000²), 4001×4000 just over limit, 16 MP zlib bomb (<1 MB), >8 MiB image,
>9 MiB body, bad Content-Length, 12,001-char text, animated PNG; AI unsafe next_step/flags
(gift-card payment instructions, HTML), AI "Looks OK" vs gift-card/secrecy rules, gift-card text only
in extracted photo text, invalid AI verdict; unreadable-image reassurance (readable false/None/"true",
empty extraction), demo image-only and benign-text+image; prompt injection in text and in photo
extraction, untrusted-role placement in prompt; 4 benign, 2 benign-FP, 4 scam, 3 evasion texts;
Timeout/ConnectionError/402/429/503/ValueError end-to-end; transport 402/429/500/503/302/204, non-JSON,
empty JSON, no-JSON content, bad verdict, truncated JSON, finish_reason=length, 80 KB stream, bad
content parts, non-object JSON, valid-but-64 KiB+ envelope, overlong extraction; endpoint pinning
(http, other host, suffix host, query, userinfo); key not in /api/config or error responses.

Mutants: M1 pixel limit, M2 picture.load, M3 magic-byte check, M4 AI next_step passthrough, M5 AI flags
passthrough, M6 AI verdict overrides rules, M7 incomplete-image guard, M8 rules ignore extracted text,
M9 AI-error keeps Looks OK, M10 invalid verdict→Looks OK, M11 finish_reason, M12 response cap,
M13 endpoint pin, M14 strict image_readable, M15 gift-card weight, M16 body limit, M17 redirects,
M18 strong-rule floor. Builder suite alone killed 13; Vex suite added M2, M10, M12.

## Findings
| ID | Severity | Finding |
|---|---|---|
| F1 | **Medium** | Rules-only (demo / no-key) false negatives return **Looks OK**: "Buy g1ft c4rds and send me the codes", zero-width "gift\u200bcards", and "Hi, this is your grandson. I need 900 dollars for a lawyer, call me at this new number." Pre-existing: `rules.py` is byte-identical to main, not introduced by this candidate. Live mode with AI failure is forced to Be Careful (verified), and Looks OK always carries "not proof it is safe" advice. Not rated High because it is the labelled rules-only demo fallback, not the AI path; still a real reassurance risk if demo mode is shown to users as a product. Recommend Unicode normalization/leet folding and a "new number / lawyer / grandson" family pattern in a future candidate. |
| F2 | Low | Benign false positives (caution direction): "small car accident but I'm fine" (3), bank "never share your pin" (3), "subscription expires next month" (2) → Be Careful. |
| F3 | Low | Test gaps: builder suite did not kill M2 (decoded-pixel load), M10 (invalid AI verdict default) or M12 (response size cap); Vex tests now cover them. M3 (magic bytes; Pillow format check is equivalent) and M18 (score≥4 floor; already implied by rule verdict ≥ Be Careful) survive as redundant defense-in-depth. |
| F4 | Low | `static/index.html` builds help line via `innerHTML` from server constant `HELP`; AI flags use `textContent`. Not exploitable now, fragile if HELP ever becomes dynamic. |
| F5 | Info | Accessibility basics present: `lang`, viewport, `aria-live`/role status, 3 labels, no alt-less images, no outline suppression, ≥20 px fonts, tel: link, speech synthesis; browser smoke covers mobile layout/keyboard/errors. No screen-reader or contrast audit performed. |
| F6 | Info | The app trusts the model's `image_readable`/`extracted_text`. A photo whose injected text makes the model lie (claims readable, omits scam words, says Looks OK) cannot be detected offline; residual model risk. |
| F7 | Info | Live report: 13/13 internally consistent; cost recomputes exactly. All 8 scam text cases and 4 of 5 photos were also caught by rules alone (rule_score ≥5), so the campaign shows little independent evidence of model value; synthetic, small, not an accuracy measure. |
| F8 | Info | **Funding evidence rests solely on the owner's statement** of $149 free promotional credit; no dashboard or invoice debit was observed by the builder or Vex. |
| F9 | Info | Windows results not reproduced (Linux only). |

No High-severity defect found: no key leakage, no AI-supplied advice or flags reach the user, rule
warnings cannot be suppressed by the AI, unreadable photos never get Looks OK, API failures never
yield Looks OK, endpoint is pinned and redirects disabled.

## Scope
This acceptance covers only the offline-verified behavior of this exact candidate on Linux.
It is **not** a deployment, merge, or hackathon submission approval and **not** an accuracy guarantee.
Remaining gates: Windows re-run, real-photo/handwriting accuracy, F1 for any demo-mode user exposure,
authenticated submission fields.

Evidence: VEX_SCAM_CHECKER_QC_EVIDENCE_20261102.zip (logs, Vex tests, mutation harness, hashes).

Signed: **Vex**, November 2, 2026

DECISION: ACCEPTED — commit 87d659b59a8d4b0bf484e02e8d10105167aef4ea, ZIP SHA-256 7fa011855b3f3cd3d0f6180029719d4adb74f669b6bd73489d78a4f3d08119b7
