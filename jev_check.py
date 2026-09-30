"""The judge is verified before it is used.

An earlier version of this work concluded that the discrete judge "does not discriminate",
and published that. It was wrong: the request had been malformed. `state` was an object
rather than a string, and a separate `options` list was sent alongside `criteria` — there is
no `options` field, the option set IS the criteria keys. A malformed spec does not error; it
returns a well-formed, confidently unhelpful answer.

So the control runs first, every time, and no experiment in this directory is believed
without it. A negative control that shares the call path of the thing it is auditing cannot
detect a fault in that path.
"""
import json, os, random, time, urllib.request, urllib.error

BASE = "https://api.typesafe.ai/v1/systemone"
KEY = os.environ.get("TYPESAFEAI_KEY", "")
MODEL = "jev-1.13.0"

def call(state, criteria, instructions, qid="q", tries=4):
    if not KEY:
        return {"error": "no TYPESAFEAI_KEY"}
    body = {"model": MODEL, "state": state,
            "questions": {qid: {"type": "choice", "instructions": instructions,
                                   "criteria": criteria}}}
    req = urllib.request.Request(
        BASE, data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
                 "Accept": "application/json", "User-Agent": "jev-fusion/1.0 (+Quilt)"})
    for a in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=50) as r:
                return json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            if e.code in (502, 503, 504) and a < tries - 1:
                time.sleep(0.5 + random.random() * 0.3); continue
            return {"error": f"HTTP {e.code}"}
        except Exception:
            if a < tries - 1:
                time.sleep(0.5); continue
            return {"error": "transport"}


def judge(state, criteria, instructions, qid="q"):
    r = call(state, criteria, instructions, qid)
    ans = (r.get("answers") or {}).get(qid)
    if not ans:
        return {"error": r.get("error", "no answer"), "p": 0.5, "argmax": None}
    p = ans.get("probabilities") or {}
    return {"argmax": max(p, key=p.get) if p else None,
            "p": round(max(p.values()) if p else 0.0, 4),
            "dist": {k: round(v, 4) for k, v in p.items()},
            "confidence": ans.get("confidence")}


VERDICT = {"true": "This statement is factually correct.",
           "false": "This statement is factually incorrect.",
           "uncertain": "There is not enough information to judge it."}

CONTROLS = [
    ("two_plus_two_four", "The number two plus two equals four.", "true"),
    ("two_plus_two_five",  "The number two plus two equals five.",  "false"),
    ("water_is_dry",       "Water is dry.",                           "false"),
    ("paris_france",       "Paris is the capital of France.",          "true"),
    ("paris_spain",        "Paris is the capital of Spain.",           "false"),
]

def self_check(verbose=True):
    ok = 0
    rows = []
    for name, state, want in CONTROLS:
        r = judge(state, VERDICT, "Is this statement true or false?")
        good = r.get("argmax") == want
        ok += good
        rows.append({"control": name, "want": want, "got": r.get("argmax"), "ok": good})
        if verbose:
            print(f"    {name:20} want {want:9} got {str(r.get('argmax')):9} {'ok' if good else 'FAIL'}")
    verdict = "JUDGE VERIFIED" if ok == len(CONTROLS) else f"JUDGE UNRELIABLE ({ok}/{len(CONTROLS)})"
    if verbose:
        print(f"  {verdict}\n")
    return ok == len(CONTROLS), rows

if __name__ == "__main__":
    print("  verifying the judge before any experiment is believed\n")
    good, rows = self_check()
    json.dump({"ok": good, "controls": rows},
              open(os.path.join(os.path.dirname(__file__), "experiments_jev_check.json"), "w"), indent=1)
    raise SystemExit(0 if good else 1)
