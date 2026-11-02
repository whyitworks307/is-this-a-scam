# Live Meta test campaign

Status: NOT RUN. No API key was available to this engineering session; promotional
credit status and personal-billing protection could not be verified. Actual usage: $0.
The previous 12/12 live result belongs to the original baseline, not this candidate.

Thirteen fictional cases are prepared in `tests/fixtures/campaign.json`: three clear
document images, two degraded images, a benign message, gift cards, government and
bank impersonation, family emergency, a suspicious link, private financial details,
and embedded adversarial instructions. These are generated photographs of synthetic
typeset pages, not camera captures or real victims' letters. Blurry/dark cases must
be cautious; any Looks OK on those cases fails. No fresh live verdict is recorded.

Before sending anything, inspect the actual Meta project billing dashboard. Confirm
at least $5 promotional credit remains and personal payment fallback is disabled.
Do not add a card, change billing settings, or buy credits. If this cannot be verified,
stop. A successful model call alone does not establish the source of its payment.

Store a local, non-secret proof JSON (outside git), using real observed values:

```json
{
  "promotional_credit_active": true,
  "personal_billing_disabled": true,
  "standard_mode_confirmed": true,
  "checked_at_utc": "[actual current ISO timestamp]",
  "promotional_balance_usd": "[observed balance]",
  "billing_evidence_reference": "[non-secret evidence location/project reference]",
  "input_usd_per_million": "1.25",
  "output_usd_per_million": "4.25"
}
```

Then, from the activated test environment with `META_API_KEY` already set and
`DEMO_MODE` unset:

```bash
python tools/live_campaign.py --billing-proof /path/to/local-proof.json
```

The runner uses exactly `muse-spark-1.3` Standard on the official HTTPS endpoint.
It allows at most 13 sequential requests, no retries, 4096 completion tokens, and
a $5 campaign maximum. Before each call it durably reserves $1.34, based on the
entire 1,048,576-token context at the uncached input price plus maximum output.
Complete usage replaces that reservation with an uncached token-price estimate.
Missing usage, a timeout, or API failure retains the reservation and stops the run.
The output file is exclusively created: do not bypass it to repeat a campaign.
This local guard relies on the checked provider rates and credit/billing evidence;
it cannot control the provider account or simultaneous use by other tools.

Official sources checked November 2, 2026:

- https://dev.meta.ai/docs/pricing-rate-limits — Standard input $1.25/M, output $4.25/M.
- https://dev.meta.ai/docs/models — Muse Spark context 1,048,576 tokens; Standard model ID.
- https://dev.meta.ai/docs/protocols/chat-completions — `max_completion_tokens` and usage fields.

Compare every actual verdict with its expected value. Report mismatches and unreadable
cases; do not relabel the ground truth to match the model. Keep model and billing
reports separate from independent QC. Run `test_samples.py` against this candidate
only within the remaining verified budget if additional live coverage is needed.
