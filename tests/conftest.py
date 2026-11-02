"""Offline tests fail closed if a real HTTP call slips past a test double."""
import pytest
import requests

@pytest.fixture(autouse=True)
def no_external_http(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError('External HTTP is forbidden in offline tests')
    monkeypatch.setattr(requests.sessions.Session, 'request', blocked)
