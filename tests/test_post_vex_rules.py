"""Permanent F1 regressions. All requests are offline and contain fictional text."""
import pytest
from fastapi.testclient import TestClient
import app
import rules

client=TestClient(app.app)
EVASIONS=[
    'Buy g1ft c4rds and send me the codes, hurry.',
    'Buy gift\u200bcards and send the codes.',
    'Buy ｇｉｆｔ ｃａｒｄｓ and send the codes.',
    'Buy gift\u2060cards and send the codes.',
    'Buy gift-card codes for the payment.',
    'Buy gift    cards for the payment.',
    "Hi, this is your grandson. I need 900 dollars for a lawyer, call me at this new number.",
    'This is your granddaughter. Send money for a lawyer to this new number.',
]

@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setenv('DEMO_MODE','1')
    monkeypatch.delenv('META_API_KEY',raising=False)

@pytest.mark.parametrize('text',EVASIONS)
def test_demo_evasion_never_reassures(text):
    r=client.post('/api/check',data={'text':text})
    assert r.status_code==200
    assert r.json()['verdict'] in ('Be Careful','Likely Scam')

@pytest.mark.parametrize('text',[
    'My grandson is a lawyer. We will see him at lunch.',
    'My granddaughter wants to visit this weekend.',
    'Invoice AB123 is ready for pickup tomorrow.',
    'Dinner is at 6.30 and the address ends in 1547.',
])
def test_normal_messages_are_not_added_false_positives(text):
    assert rules.precheck(text)['verdict']=='Looks OK'

def test_curly_apostrophe_secrecy_still_warns():
    assert rules.precheck('Don\u2019t tell anyone.')['score']>=4

def test_money_digits_not_rewritten_by_normalization():
    assert '1234.56' in rules.normalized_text('Invoice AB123: 1234.56')

@pytest.mark.parametrize('text',EVASIONS[:2])
def test_extracted_evasion_survives_false_safe_ai(monkeypatch,text):
    monkeypatch.setenv('DEMO_MODE','0')
    monkeypatch.setenv('META_API_KEY','FAKE_TEST_VALUE_NOT_A_SECRET')
    monkeypatch.setattr(app.meta_client,'analyze',lambda *args:{'verdict':'Looks OK','flags':[],
        'next_step':'Pay now','extracted_text':text,'image_readable':True})
    from test_hardening import PNG
    r=client.post('/api/check',files={'image':('letter.png',PNG,'image/png')}).json()
    assert r['verdict'] in ('Be Careful','Likely Scam')
    assert 'Pay now' not in str(r)
