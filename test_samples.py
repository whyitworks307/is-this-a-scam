"""Runs every sample through the live server and checks the verdict."""
import json, sys, requests
base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
ok = 0
samples = json.load(open("samples.json"))
for s in samples:
    r = requests.post(base + "/api/check", data={"text": s["text"]}).json()
    good = r["verdict"] == s["expected"]
    ok += good
    print(f"{'PASS' if good else 'FAIL'}  {s['id']:15} expected={s['expected']:12} got={r['verdict']:12} score={r['rule_score']}")
print(f"{ok}/{len(samples)} passed")
sys.exit(0 if ok == len(samples) else 1)
