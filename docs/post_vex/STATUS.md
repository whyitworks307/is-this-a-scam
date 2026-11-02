# Post-Vex follow-up — November 2, 2026

Status: BUILDER VERIFIED, PENDING NEW VEX REVIEW. Not merged, deployed, or submitted.

Vex accepted only parent commit `87d659b59a8d4b0bf484e02e8d10105167aef4ea`, ZIP
SHA-256 `7fa011855b3f3cd3d0f6180029719d4adb74f669b6bd73489d78a4f3d08119b7`,
for Linux offline behavior. Its report is preserved unchanged as
`VEX_ACCEPTED_PARENT_REPORT.md`. That decision does not transfer to this successor.

## Demonstrated findings addressed

- F1, Medium: rules-only demo could say Looks OK for `g1ft c4rds`, zero-width
  gift-card text, and a grandson asking for lawyer money. Matching now applies
  Unicode NFKC, removes invisible formatting controls, recognizes a small fixed
  set of leet-spelled warning words, and handles hyphen/space variants of gift
  cards. A bounded family-member/request/money pattern catches the lawyer case.
  Numeric amounts and unrelated identifiers are not rewritten. Normalization is
  only for deterministic matching; the displayed and model-supplied message is unchanged.
- F3, Low: Vex's unchanged 74-case adversarial suite is now a permanent regression.
  It covers the prior decoded-pixel, invalid-verdict, and reply-size test gaps.
- F4, Low: help metadata is built with text nodes and a fixed `tel:` link rather
  than `innerHTML`. A browser check displays hostile metadata literally.

The original 12 rule categories and their weights remain. F2's conservative
benign false positives are retained; no broad suppression was added. Model
transcription/readability remains an unverified model judgment (F6). Funding
evidence remains the owner's earlier confirmation, not a dashboard audit (F8).
Real-camera/handwriting accuracy and a screen-reader audit remain unmeasured.

## Evidence

- Before repair: the unchanged Vex suite reproduced 72 pass / 2 expected failures.
  New mandatory F1 regressions also reproduced the missed warnings.
- After repair: 191/191 tests pass on Linux and Windows; all 74 unchanged Vex cases pass with
  no xfails. The new regressions require a cautious verdict rather than allowing
  a known miss to be recorded as an expected failure.
- Original sample runner: 12/12 in demo mode.
- Chromium: 16/16 browser checks, including safe help metadata rendering.
- Targeted mutation checks: 5/5 detected. These are fresh builder checks covering
  decoded pixels, invalid verdict, response cap, normalization, and family request
  matching. They are separate from Vex's original 18-mutant parent review.
- Windows results are recorded separately under `evidence/post_vex/`; reproducing
  Vex-authored tests on Windows is builder evidence, not independent Windows QC.
  All 65 source files in the corrected Windows staging packet were hash-checked.
  An earlier staging attempt omitted the test-support `tools/` directory and
  failed test collection; that packaging error was corrected before the clean run.
- New live API calls: 0. Additional promotional use: $0. Prior combined estimate
  remains $0.46297250. Existing demo, video, voiceover, submission draft, samples,
  accepted archives, and Personal Relay were not changed.

The 13-case parent live campaign has not been rerun on this successor. Its report
must not be relabeled as a fresh live test. No release/deployment approval is implied.

## Vex handoff

Review branch `post-vex-scam-fixes-20261102` and record the exact frozen commit/ZIP
pin in the accompanying delivery file. Compare only with accepted parent 87d659b.
Independently reproduce the new F1 cases, unchanged Vex suite, original samples,
help-text browser test, and five targeted mutations. Check normal-message regressions
and retained limits. Issue ACCEPTED or REJECTED for the new pin with scope and evidence.

The November 4, 2026, 8 PM Central deadline remains. Keep the accepted parent available
while this successor awaits review; do not delay submission for further features.
