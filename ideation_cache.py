"""DeepInfra lane, built to make the cache do the work.

THE STRATEGY. A per-token cache means the cost of a call is dominated by whatever is NEW.
So: one long shared DOSSIER, sent verbatim on every call, and a short question after it.
The first call pays for the dossier; every call after it is nearly all cache hits. Running
many short questions against the same dossier is therefore far cheaper than the same number
of standalone questions, and the answers are BETTER because each one sees the same
grounded context.

THE OTHER HALF: one model, one topic, many rounds. Switching models every call throws away
the context and re-derives the framing. Staying on one model for a run means the later
questions are answered by a model that has already absorbed the dossier, and the
disagreements between rounds are the interesting signal rather than noise.

`ByteDance/Seed-2.0-mini` is the cheap workhorse here. The lane is for breadth and
ideation, not authority; anything that looks load-bearing gets re-derived elsewhere.
"""
import os, json, urllib.request, urllib.error, time, hashlib

BASE = "https://api.deepinfra.com/v1/chat/completions"
KEY = os.environ.get("DEEPINFRA_TOKEN", "")
MODEL = os.environ.get("DI_MODEL", "ByteDance/Seed-2.0-mini")

DOSSIER = """\
You are advising a substrate research programme. Here is what has been established, with
its evidence status, so you do not have to re-derive it.

A cellular substrate where the canonical unit is a cell graph and the algebra is
BIND/LINK/EFFECT/VIEW/TICK plus six adopted opcodes. Polyformalism: the same canary in
many languages, so no single port can carry the whole river. The canon gate is a chord
across several models, not one vote. Cells are scars, not parameters. The witness log is
prediction wearing the costume of archive.

ESTABLISHED, with controls:
- A fast discrete decision model (typed probabilities) CAN separate classes cleanly. An
  earlier published null saying otherwise was our own malformed request, now retracted.
- That same model gates a self-decomposing loop: given only a case and a description of an
  already-compiled class (never asked whether an answer is right), it reads membership
  correctly. Its bias is to keep calling the model, which is the safe direction.
- A discrete judge selecting which cells to correct in a generative field is
  statistically indistinguishable from a FREE local-noise heuristic, and 56% worse than an
  oracle ceiling, for ~100 model calls per field.
- A d-dimensional opinion space sustains d+1 well-separated "tissues" under one local rule.
  2-D refuses a fourth opinion; 3-D holds four. 1-D is bimodal.
- Whether an intensity alphabet is sufficient depends on its ALIGNMENT, not its size: two
  materials 5 luma apart collide at some quantisations and separate at others.
- Brightness-only encoding is a rank-one projection and cannot distinguish materials that
  render equally bright, at any alphabet size.

FAILED, and worth more than the successes:
- Averaging beliefs has a fixed point at the prior. A swarm that averages converges to
  undecided and stays there.
- Similarity gating cannot carry a belief across a gap.
- A "tissue" that dissolves when kicked and does not reform is a transient, not a structure.
- Three separate controls were broken in the same way: a control that shares the call path of
  the thing it audits agrees with the bug; a control that reshuffles rows carrying their own
  labels is a tautology; a pipeline ending in `tail` reports success while the upstream
  process crashed.

QUESTION: """


def ask(question, timeout=90, model=None, dossier=DOSSIER):
    if not KEY:
        return {"error": "no DEEPINFRA_TOKEN"}
    body = {"model": model or MODEL,
            "messages": [{"role": "user", "content": dossier + question}],
            "temperature": 0.8, "max_tokens": 900}
    req = urllib.request.Request(
        BASE, data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
                 "User-Agent": "jev-fusion-ideation/1.0"})
    for a in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read() or b"{}")
            return {"text": d["choices"][0]["message"]["content"],
                    "usage": d.get("usage", {})}
        except urllib.error.HTTPError as e:
            if e.code in (502, 503, 504, 429) and a < 2:
                time.sleep(2 + 2 * a); continue
            return {"error": f"HTTP {e.code}"}
        except Exception:
            if a < 2:
                time.sleep(2); continue
            return {"error": "transport"}


if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else \
        "What is the single most promising experiment we have NOT run, and what would falsify it?"
    t0 = time.time()
    r = ask(q)
    dt = time.time() - t0
    if r.get("error"):
        print("  error:", r["error"]); raise SystemExit(1)
    u = r.get("usage", {})
    print(f"  model {MODEL}  {dt:.1f}s")
    print(f"  usage: prompt {u.get('prompt_tokens')} completion {u.get('completion_tokens')}"
          f"{'  CACHE HIT' if u.get('cache_read_input_tokens') else ''}")
    print()
    print(r["text"])
