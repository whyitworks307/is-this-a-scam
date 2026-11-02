"""Explicitly gated Standard-mode test runner. Never stores keys or raw HTTP.

This cannot verify provider billing itself. A human/operator must first inspect
the actual Meta project billing page and supply current, non-secret evidence.
No request is sent until that condition and all local gates are satisfied.
"""
import argparse
from datetime import datetime, timezone
from decimal import Decimal
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import app
import meta_client
from fastapi.testclient import TestClient

BUDGET = Decimal('5.00')
MAX_REQUESTS = 13
# Full 1,048,576-token model context at the uncached Standard input rate,
# plus 4096 output tokens, rounded UP. Conservative even for unknown image use.
RESERVE = Decimal('1.34')
INPUT_RATE, OUTPUT_RATE = Decimal('1.25'), Decimal('4.25')

def validate_proof(proof):
    required = ['promotional_credit_active', 'standard_mode_confirmed']
    if any(proof.get(k) is not True for k in required):
        raise ValueError('Promotional-only billing and Standard mode must be verified on the actual project.')
    checked = datetime.fromisoformat(proof['checked_at_utc'].replace('Z', '+00:00'))
    age = (datetime.now(timezone.utc) - checked).total_seconds()
    if not 0 <= age <= 7200:
        raise ValueError('Billing verification must be less than two hours old.')
    if Decimal(str(proof['promotional_balance_usd'])) < BUDGET:
        raise ValueError('At least $5 in promotional credit must remain.')
    # A current, explicit account-owner confirmation of ample promotional credit
    # is usable evidence; do not invent a claim that billing settings were changed.
    # Keep a two-campaign margin ($10) even though this campaign may spend only $5.
    if proof.get('personal_billing_disabled') is not True and not (
        proof.get('credit_verification_source') == 'explicit_user_confirmation'
        and Decimal(str(proof['promotional_balance_usd'])) >= Decimal('10.00')
    ):
        raise ValueError('Verify promotional funding or disabled personal billing before any request.')
    if not proof.get('billing_evidence_reference'):
        raise ValueError('A non-secret project billing evidence reference is required.')
    if proof.get('input_usd_per_million') != '1.25' or proof.get('output_usd_per_million') != '4.25':
        raise ValueError('Recheck the current official Standard pricing before this campaign.')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--billing-proof', type=Path, required=True)
    p.add_argument('--out', type=Path, default=ROOT/'live_results')
    args = p.parse_args()
    # All gates run BEFORE a real call or server launch.
    validate_proof(json.loads(args.billing_proof.read_text()))
    if not meta_client.api_key():
        raise ValueError('META_API_KEY is not set in this process. Do not paste it into chat.')
    if meta_client.MODEL != 'muse-spark-1.3' or meta_client.API_BASE.rstrip('/') != 'https://api.meta.ai/v1':
        raise ValueError('Only official Muse Spark 1.3 Standard mode is allowed.')
    if os.getenv('DEMO_MODE', '').lower() in ('1', 'true', 'yes'):
        raise ValueError('Unset DEMO_MODE for the live experiment.')
    cases = json.loads((ROOT/'tests/fixtures/campaign.json').read_text())
    if len(cases) > MAX_REQUESTS:
        raise ValueError('Request count exceeds campaign limit.')
    args.out.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents rerunning or overlapping the same campaign.
    ledger_path = args.out/'campaign.json'
    fd = os.open(ledger_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    state = {'status': 'RUNNING', 'requests_started': 0, 'cost_reserved_or_measured_usd': '0', 'results': []}
    def save():
        ledger_path.write_text(json.dumps(state, indent=2)+'\n')
    os.close(fd)
    spent = Decimal('0')
    original = meta_client.analyze
    captured = {}
    def measured(*a):
        captured.clear()
        result = original(*a)
        captured.update(result)
        return result
    meta_client.analyze = measured
    try:
        with TestClient(app.app) as client:
            for case in cases:
                if spent + RESERVE > BUDGET:
                    state['status'] = 'STOPPED_BUDGET'
                    break
                state['requests_started'] += 1
                spent += RESERVE  # Reserve BEFORE dispatch; a crash keeps this debit.
                state['cost_reserved_or_measured_usd'] = str(spent)
                save()
                files = None
                if case.get('image'):
                    import hashlib
                    photo = (ROOT/case['image']).read_bytes()
                    if hashlib.sha256(photo).hexdigest() != case['sha256']:
                        raise ValueError('Synthetic image hash mismatch')
                    files = {'image': ('synthetic.jpg', photo, 'image/jpeg')}
                start = time.monotonic()
                response = client.post('/api/check', data={'text': case['text']}, files=files)
                actual = response.json()
                usage = captured.get('_usage', {})
                complete = all(type(usage.get(k)) is int for k in ('prompt_tokens', 'completion_tokens'))
                if complete:
                    cost = (usage['prompt_tokens']*INPUT_RATE + usage['completion_tokens']*OUTPUT_RATE)/1_000_000
                    if cost > RESERVE:
                        raise ValueError('Usage exceeded conservative bound; stop and recheck pricing.')
                    spent += cost - RESERVE
                row = {'id': case['id'], 'expected': case['expected'], 'actual': actual,
                       'pass': response.status_code == 200 and actual.get('verdict') in case['expected'] and not actual.get('ai_error'),
                       'elapsed_seconds': round(time.monotonic()-start, 3), 'usage': usage,
                       'cost_basis': 'measured_tokens' if complete else 'conservative_reservation'}
                state['results'].append(row)
                state['cost_reserved_or_measured_usd'] = str(spent)
                save()
                if actual.get('ai_error') or not complete:
                    state['status'] = 'STOPPED_API_OR_USAGE_UNKNOWN'
                    break  # No automatic retries after an uncertain/failed call.
                time.sleep(1)  # Sequential, at most one request per second.
            else:
                state['status'] = 'COMPLETE'
    finally:
        meta_client.analyze = original
        save()
    print(json.dumps({'status': state['status'], 'requests_started': state['requests_started'],
                      'cost_reserved_or_measured_usd': state['cost_reserved_or_measured_usd']}))
    return 0 if state['status'] == 'COMPLETE' and all(r['pass'] for r in state['results']) else 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        # Do not print transport exceptions, headers, credentials, or source docs.
        print('Campaign blocked or stopped: ' + (str(exc) if isinstance(exc, (ValueError, FileExistsError)) else type(exc).__name__))
        sys.exit(2)
