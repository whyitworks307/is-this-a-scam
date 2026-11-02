"""Headless Chromium checks. Install playwright separately; uses demo only."""
import json
import os
from pathlib import Path
import socket
import subprocess
import time
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]

def main():
    python = ROOT/'.venv/bin/python'
    if os.name == 'nt':
        python = ROOT/'.venv/Scripts/python.exe'
    server = subprocess.Popen([str(python), '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', '8123'],
        cwd=ROOT, env=dict(os.environ, DEMO_MODE='1', META_API_KEY=''), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    checks = []
    def passed(name):
        checks.append({'check': name, 'status': 'PASS'})
    try:
        for _ in range(100):
            try:
                with socket.create_connection(('127.0.0.1', 8123), timeout=.2):
                    break
            except OSError:
                time.sleep(.05)
        else:
            raise RuntimeError('Demo server did not start')
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
            page = browser.new_page()
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.route('**/*', lambda route: route.continue_() if route.request.url.startswith('http://127.0.0.1:8123/') else route.abort())
            page.goto('http://127.0.0.1:8123/')
            expect(page.get_by_role('heading', name='Is This a Scam?', exact=True)).to_be_visible()
            expect(page.locator('#demo')).to_be_visible()
            expect(page.locator('#samples option')).to_have_count(13)
            passed('Demo page and all twelve sample choices load')
            expect(page.get_by_label('1. Paste the message here:')).to_be_visible()
            assert page.locator('#img').get_attribute('aria-describedby') == 'photo-help'
            assert page.locator('#msg').get_attribute('maxlength') == '12000'
            passed('Input labels, photo help, and text limit')
            page.get_by_role('button', name='Check It', exact=True).click()
            expect(page.get_by_role('alert')).to_contain_text('Please paste')
            passed('Empty-input error is announced inline')
            page.locator('#samples').select_option('giftcard')
            page.locator('#check').click()
            expect(page.locator('#verdict')).to_contain_text('Likely Scam')
            expect(page.locator('#result')).to_be_focused()
            passed('Scam result, safe action, and keyboard focus')
            page.evaluate("()=>{window.__spoken=[]; speechSynthesis.speak=u=>window.__spoken.push(u.text);}")
            page.locator('#speak').click()
            assert 'Likely Scam' in page.evaluate('window.__spoken[0]')
            assert "Don't pay" in page.evaluate('window.__spoken[0]')
            passed('Read Out Loud receives the reviewed result text')
            assert 'Can you help me?' in page.evaluate('summary()')
            passed('Family-share draft contains result and request for help; nothing sent')
            page.locator('#samples').select_option('legit_family')
            page.locator('#check').click()
            expect(page.locator('#verdict')).to_contain_text('Looks OK')
            expect(page.locator('#step')).to_contain_text('not proof')
            passed('Benign sample retains safe-verdict caveat')
            page.locator('#img').set_input_files({'name':'bad.png','mimeType':'image/png','buffer':b'\x89PNG\r\n\x1a\nBAD'})
            page.locator('#check').click()
            expect(page.locator('#error')).to_contain_text('could not be opened')
            expect(page.locator('#check')).to_be_enabled()
            expect(page.locator('#result')).not_to_be_visible()
            passed('Invalid photo error hides old verdict and restores controls')
            page.locator('#samples').select_option('irs')
            assert page.locator('#img').evaluate('(el)=>el.files.length') == 0
            passed('Choosing a sample clears a previous photo')
            def delayed(route):
                expect(page.locator('#check')).to_be_disabled()
                expect(page.locator('#msg')).to_be_disabled()
                assert page.locator('#check').get_attribute('aria-busy') == 'true'
                route.fulfill(status=503, json={'detail':'The checker is unavailable. Try again.'})
            page.route('**/api/check', delayed)
            page.locator('#check').click()
            expect(page.locator('#error')).to_contain_text('unavailable')
            expect(page.locator('#check')).to_be_enabled()
            passed('In-flight controls lock and HTTP failure restores them')
            page.unroute('**/api/check', delayed)
            page.route('**/api/check', lambda r:r.fulfill(status=502, body='not json'))
            page.locator('#check').click()
            expect(page.locator('#error')).to_contain_text('could not answer')
            expect(page.locator('#check')).to_be_enabled()
            passed('Non-JSON gateway error is readable and recoverable')
            page.unroute('**/api/check')
            page.route('**/api/check', lambda r:r.abort())
            page.locator('#check').click()
            expect(page.locator('#error')).not_to_be_empty()
            expect(page.locator('#check')).to_be_enabled()
            passed('Network failure restores controls')
            page.unroute('**/api/check')
            for width in (360, 320):
                page.set_viewport_size({'width':width, 'height':800})
                page.locator('#check').click()
                expect(page.locator('#verdict')).to_contain_text('Likely Scam')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                passed(f'No horizontal overflow at {width}px')
            assert not errors, errors
            passed('No uncaught page JavaScript errors')
            browser.close()
    finally:
        server.terminate()
        server.wait(timeout=5)
        (ROOT/'evidence/browser_smoke.json').write_text(json.dumps(checks, indent=2)+'\n')
    print(f'{len(checks)} browser checks passed')

if __name__ == '__main__':
    main()
