"""Cost gates must reject before any real model request."""
from datetime import datetime, timezone, timedelta
import pytest
from tools.live_campaign import validate_proof, RESERVE, BUDGET

def proof():
    return dict(promotional_credit_active=True, personal_billing_disabled=True,
                standard_mode_confirmed=True, checked_at_utc=datetime.now(timezone.utc).isoformat(),
                promotional_balance_usd='150.00', billing_evidence_reference='SYNTHETIC_TEST_ONLY',
                input_usd_per_million='1.25', output_usd_per_million='4.25')

@pytest.mark.parametrize('field', ['promotional_credit_active', 'personal_billing_disabled', 'standard_mode_confirmed'])
def test_billing_verification_required(field):
    p = proof()
    p[field] = False
    with pytest.raises(ValueError):
        validate_proof(p)

def test_stale_verification_rejected():
    p = proof()
    p['checked_at_utc'] = (datetime.now(timezone.utc)-timedelta(hours=3)).isoformat()
    with pytest.raises(ValueError):
        validate_proof(p)

def test_low_credit_rejected():
    p = proof()
    p['promotional_balance_usd'] = '4.99'
    with pytest.raises(ValueError):
        validate_proof(p)

def test_valid_proof_format_only():
    # Validates the format; this does NOT prove real credits are available.
    validate_proof(proof())
    assert RESERVE < BUDGET

def test_explicit_owner_credit_confirmation_does_not_claim_billing_disabled():
    p = proof()
    p['personal_billing_disabled'] = False
    p['credit_verification_source'] = 'explicit_user_confirmation'
    p['promotional_balance_usd'] = '149.00'
    validate_proof(p)

def test_owner_confirmation_requires_two_campaign_margin():
    p = proof()
    p['personal_billing_disabled'] = False
    p['credit_verification_source'] = 'explicit_user_confirmation'
    p['promotional_balance_usd'] = '9.99'
    with pytest.raises(ValueError):
        validate_proof(p)

def test_synthetic_manifest_hashes():
    import hashlib, json
    from tools.live_campaign import ROOT, MAX_REQUESTS
    rows = json.loads((ROOT/'tests/fixtures/campaign.json').read_text())
    assert len(rows) == MAX_REQUESTS == 13
    for row in rows:
        if row.get('image'):
            assert hashlib.sha256((ROOT/row['image']).read_bytes()).hexdigest() == row['sha256']
