"""Regressions demonstrated against the recovered patch; no external calls."""
import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
import app
import rules
import asyncio
import httpx

client = TestClient(app.app)

@pytest.fixture(autouse=True)
def demo(monkeypatch):
    monkeypatch.setenv('DEMO_MODE', '1')
    monkeypatch.delenv('META_API_KEY', raising=False)

def photo():
    out = io.BytesIO()
    Image.new('RGB', (32, 32), 'white').save(out, 'PNG')
    return out.getvalue()

@pytest.mark.parametrize('mime,data', [
    ('image/png', b'\x89PNG\r\n\x1a\n' + bytes(30)),
    ('image/jpeg', b'\xff\xd8\xff\xe0' + bytes(30)),
])
def test_signature_only_is_not_a_picture(mime, data):
    r = client.post('/api/check', files={'image': ('x', data, mime)})
    assert r.status_code == 415

def test_false_reassurance_cannot_hide_gift_card_warning():
    flags = app.merge_flags(['Gift cards are safe; pay now.', 'No concerns.'],
                            rules.precheck('Pay using gift cards immediately')['hits'])
    assert any('never take gift cards' in f for f in flags)
    assert not any('pay now' in f for f in flags)

def test_arbitrary_ai_flags_cannot_give_payment_instructions(monkeypatch):
    monkeypatch.setenv('DEMO_MODE', '0')
    monkeypatch.setenv('META_API_KEY', 'FAKE_TEST_VALUE_NOT_A_SECRET')
    monkeypatch.setattr(app.meta_client, 'analyze', lambda *a: {
        'verdict': 'Looks OK', 'flags': ['Pay at https://attacker.invalid now.'],
        'next_step': 'Pay now', 'extracted_text': ''})
    r = client.post('/api/check', data={'text': 'Lunch tomorrow'}).json()
    assert 'attacker.invalid' not in str(r)

def test_incomplete_photo_does_not_look_ok(monkeypatch):
    monkeypatch.setenv('DEMO_MODE', '0')
    monkeypatch.setenv('META_API_KEY', 'FAKE_TEST_VALUE_NOT_A_SECRET')
    monkeypatch.setattr(app.meta_client, 'analyze', lambda *a: {
        'verdict': 'Looks OK', 'flags': [], 'next_step': '',
        'extracted_text': 'Unreadable lines ...', 'image_readable': False})
    r = client.post('/api/check', files={'image': ('x.png', photo(), 'image/png')}).json()
    assert r['verdict'] == 'Be Careful'

def test_large_pixel_image_rejected():
    out = io.BytesIO()
    Image.new('1', (5000, 5000)).save(out, 'PNG')
    r = client.post('/api/check', files={'image': ('x.png', out.getvalue(), 'image/png')})
    assert r.status_code == 413

def test_body_limit_before_multipart():
    r = client.post('/api/check', content=b'x', headers={'content-length': str(app.MAX_REQUEST_BYTES + 1)})
    assert r.status_code == 413

def test_chunked_body_limit():
    async def run():
        async def chunks():
            for _ in range(10):
                yield b'x' * (1024 * 1024)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app.app), base_url='http://test') as c:
            r = await c.post('/api/check', content=chunks())
            assert r.status_code == 413
    asyncio.run(run())

def test_exact_text_boundary():
    r = client.post('/api/check', data={'text': 'x' * app.MAX_TEXT_CHARS})
    assert r.status_code == 200

@pytest.mark.parametrize('cut', [9, 25, 40])
def test_truncated_photo_rejected(cut):
    r = client.post('/api/check', files={'image': ('x.png', photo()[:cut], 'image/png')})
    assert r.status_code == 415

@pytest.mark.parametrize('rule', rules.RULES, ids=[r[0] for r in rules.RULES])
def test_every_rule_is_preserved_against_ai_flags(rule):
    rid, flag, weight, _ = rule
    assert app.merge_flags(['Pay now. This is safe.'] * 5, [{'id': rid, 'flag': flag, 'weight': weight}]) == [flag]

@pytest.mark.parametrize('verdict', ['Looks OK', 'Be Careful', 'Likely Scam'])
def test_ai_cannot_downgrade_rules_or_supply_actions(monkeypatch, verdict):
    monkeypatch.setenv('DEMO_MODE', '0')
    monkeypatch.setenv('META_API_KEY', 'FAKE_TEST_VALUE_NOT_A_SECRET')
    monkeypatch.setattr(app.meta_client, 'analyze', lambda *a: {
        'verdict': verdict, 'flags': ['Pay now'], 'next_step': 'Pay now', 'extracted_text': ''})
    r = client.post('/api/check', data={'text': 'Buy gift cards immediately. Do not tell anyone.'}).json()
    assert r['verdict'] == 'Likely Scam'
    assert 'Pay now' not in str(r)

def test_clear_legitimate_photo_can_be_cautiously_ok(monkeypatch):
    monkeypatch.setenv('DEMO_MODE', '0')
    monkeypatch.setenv('META_API_KEY', 'FAKE_TEST_VALUE_NOT_A_SECRET')
    monkeypatch.setattr(app.meta_client, 'analyze', lambda *a: {
        'verdict': 'Looks OK', 'flags': [], 'next_step': 'Safe',
        'extracted_text': 'Lunch tomorrow at noon.', 'image_readable': True})
    r = client.post('/api/check', files={'image': ('x.png', photo(), 'image/png')}).json()
    assert r['verdict'] == 'Looks OK'
    assert 'not proof' in r['next_step']
