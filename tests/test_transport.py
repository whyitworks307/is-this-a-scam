"""Exercise the actual Meta client and application fallback with fake HTTP."""
import json
import requests
import pytest
from fastapi.testclient import TestClient
import app
import meta_client

client = TestClient(app.app)
SAFE = {'verdict': 'Looks OK', 'flags': [], 'extracted_text': '', 'image_readable': False}

class Reply:
    def __init__(self, body, status=200):
        self.body = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.status_code, self.closed = status, False
    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError('DO_NOT_EXPOSE_INTERNAL_SENTINEL')
    def iter_content(self, size):
        for i in range(0, len(self.body), size):
            yield self.body[i:i+size]
    def close(self):
        self.closed = True

def envelope(content=SAFE, finish='stop'):
    return {'choices': [{'message': {'content': json.dumps(content)}, 'finish_reason': finish}],
            'usage': {'prompt_tokens': 250, 'completion_tokens': 60, 'total_tokens': 310}}

@pytest.fixture(autouse=True)
def live_env(monkeypatch):
    monkeypatch.setenv('META_API_KEY', 'FAKE_TEST_VALUE_NOT_A_SECRET')
    monkeypatch.setenv('DEMO_MODE', '0')

@pytest.mark.parametrize('status', [302, 400, 401, 402, 403, 413, 429, 500, 502, 503, 504])
def test_http_failures_are_cautious_and_redacted(monkeypatch, status):
    reply = Reply(envelope(), status)
    monkeypatch.setattr(meta_client.requests, 'post', lambda *a, **kw: reply)
    r = client.post('/api/check', data={'text': 'See you at noon'}).json()
    assert r['verdict'] == 'Be Careful'
    assert r['source'] == 'rules (AI call failed)'
    assert 'SENTINEL' not in str(r)
    assert reply.closed

@pytest.mark.parametrize('error', [requests.Timeout, requests.ConnectionError, requests.ReadTimeout])
def test_network_failure_uses_cautious_fallback(monkeypatch, error):
    def fail(*a, **kw):
        raise error('DO_NOT_EXPOSE_INTERNAL_SENTINEL')
    monkeypatch.setattr(meta_client.requests, 'post', fail)
    r = client.post('/api/check', data={'text': 'Pay gift cards immediately'}).json()
    assert r['verdict'] == 'Likely Scam'
    assert 'SENTINEL' not in str(r)

@pytest.mark.parametrize('body', [b'not JSON', b'[]', b'{}', b'{"choices":[]}',
    b'{"choices":[{"message":{"content":null},"finish_reason":"stop"}]}',
    b'{"choices":[{"message":{"content":[23]},"finish_reason":"stop"}]}',
    json.dumps(envelope(finish='length')).encode(),
    json.dumps(envelope(finish='content_filter')).encode(),
    b'x' * (meta_client.MAX_RESPONSE_BYTES + 1)])
def test_unexpected_response_falls_back(monkeypatch, body):
    reply = Reply(body)
    monkeypatch.setattr(meta_client.requests, 'post', lambda *a, **kw: reply)
    r = client.post('/api/check', data={'text': 'Lunch tomorrow'}).json()
    assert r['verdict'] == 'Be Careful'
    assert reply.closed

def test_request_shape_usage_and_secret_boundary(monkeypatch):
    reply = Reply(envelope())
    sent = []
    def post(url, **kwargs):
        sent.append((url, kwargs))
        return reply
    monkeypatch.setattr(meta_client.requests, 'post', post)
    result = meta_client.analyze('Lunch tomorrow', None, None, [])
    url, opts = sent[0]
    assert url == 'https://api.meta.ai/v1/chat/completions'
    assert opts['json']['max_completion_tokens'] == 4096
    assert opts['allow_redirects'] is False
    assert opts['stream'] is True
    assert opts['timeout'] == (5, 60)
    assert 'FAKE_TEST_VALUE_NOT_A_SECRET' not in str(opts['json'])
    assert result['_usage']['total_tokens'] == 310
    assert reply.closed

@pytest.mark.parametrize('base', ['http://api.meta.ai/v1', 'https://attacker.invalid/v1',
    'https://api.meta.ai@attacker.invalid/v1', 'https://api.meta.ai/v1?copy=1'])
def test_endpoint_override_cannot_export_key(monkeypatch, base):
    monkeypatch.setattr(meta_client, 'API_BASE', base)
    with pytest.raises(ValueError):
        meta_client.analyze('Lunch', None, None, [])

@pytest.mark.parametrize('value', ['true', 1, None, {}, []])
def test_readability_requires_boolean_true(value):
    assert not meta_client._parse_json(json.dumps(dict(SAFE, image_readable=value)))['image_readable']

def test_truncated_extraction_is_failure():
    with pytest.raises(ValueError):
        meta_client._parse_json(json.dumps(dict(SAFE, extracted_text='x'*12001)))

def test_content_parts_supported(monkeypatch):
    data = envelope()
    data['choices'][0]['message']['content'] = [{'type': 'text', 'text': json.dumps(SAFE)}]
    monkeypatch.setattr(meta_client.requests, 'post', lambda *a, **kw: Reply(data))
    assert meta_client.analyze('Lunch', None, None, [])['verdict'] == 'Looks OK'
