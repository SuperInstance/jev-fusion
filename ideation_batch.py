"""Run several questions against the SAME dossier. The dossier is the cache."""

import json, time, sys, os
from ideation_cache import ask, DOSSIER, MODEL

QUESTIONS = [
 "What is the single most promising experiment we have NOT run, and what would falsify it?",
 "Name the three places where our reasoning is most likely to be wrong, and why each is hard to see.",
 "What is the strongest steel-man against the claim that a discrete judge can usefully govern a continuous generative process? Give the best version of the objection and the best available reply.",
 "If you had to delete one experiment from the programme because it taught us nothing, which and why?",
 "What would a researcher outside this programme notice that we are structurally unable to?",
 "What is the cheapest experiment that could show the whole research direction is wrong?",
]

if __name__ == "__main__":
    print(f"  cache-gamed batch against one model ({MODEL}) and one shared dossier")
    print(f"  dossier = {len(DOSSIER)} chars, sent verbatim on every call\n")
    print(f"  {'#':>2}  {'secs':>6}  {'prompt':>8}  {'completion':>11}  cache_read")
    out = []
    for i, q in enumerate(QUESTIONS, 1):
        t0 = time.time()
        r = ask(q)
        dt = time.time() - t0
        if r.get("error"):
            print(f"  {i:>2}  ERROR {r['error']}")
            continue
        u = r.get("usage", {})
        cr = u.get("cache_read_input_tokens", 0) or u.get("cached_tokens", 0) or 0
        print(f"  {i:>2}  {dt:>6.1f}  {u.get('prompt_tokens','?'):>8}  "
              f"{u.get('completion_tokens','?'):>11}  {cr}")
        out.append({"q": q, "a": r["text"], "usage": u, "secs": round(dt, 1)})
    json.dump(out, open("ideation_batch.json", "w"), indent=1)
    print("\n  -> ideation_batch.json")
