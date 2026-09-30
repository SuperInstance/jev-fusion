"""Experiment 4 -- does spending compute only where a fast judge flags actually work?

THE CLAIM (alternating System 1 / System 2). A cheap pass produces a rough layout. A fast
discrete judge reads it, emits a mask of which coordinates need correction, and the expensive
backbone spends a high-precision pass only there. Claim: equal or better quality than a full
N-step pass, at a fraction of the compute.

THE PART THAT IS ACTUALLY TESTABLE is SELECTION, not image quality. Even with a real
diffusion backbone, the whole method reduces to one question: **given a fixed correction
budget, is the judge's flag better than the alternatives at choosing where to spend it?**
That is a measurable selection problem, and it needs no GPU.

SURROGATE GENERATOR. A field is denoised by repeated local smoothing toward a target field
whose ground truth is known exactly. Correcting one cell costs one unit of budget. Three
selectors, same budget:

  ORACLE  spend on the cells with the largest true error      (the upper bound)
  JUDGE   spend on the cells the discrete judge flags        (the claim)
  RANDOM  spend on uniformly random cells                    (the null)
  WORST-NOISE spend on the cells that look most locally noisy (the cheap proxy)

The honest question is not whether JUDGE beats RANDOM — anyone believes a signal beats
noise. It is **whether JUDGE approaches ORACLE**. If it does, selective refinement is worth
building. If it lands near RANDOM, the whole paradigm is a fancy way of spending compute at
random, and no amount of diffusion quality will rescue it.

THE CONTROL: ORACLE is by construction the best possible selector, so it bounds the result
from above. If JUDGE is close to ORACLE, the gap that remains is the judge's error rate and
nothing else, which is the number an implementer needs.
"""
import sys, os, random, statistics as st, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jev_check import judge, self_check

N = 10                      # grid is N x N
SMOOTH = 12                 # denoising passes
BUDGETS = [4, 8, 16, 24, 40]
SEEDS = [3, 7]                 # 2 seeds x 100 cells = 200 judge calls, ranked once and reused

CRIT = {
    "correct":  "This cell already matches what the scene calls for; correcting it would waste compute.",
    "needs_fix": "This cell does not match what the scene calls for and should be corrected.",
}

def target(rng):
    """A smooth target field plus a few deliberately wrong cells."""
    t = [[0.0] * N for _ in range(N)]
    for y in range(N):
        for x in range(N):
            t[y][x] = 0.5 + 0.35 * math.sin(x * 0.5) * math.cos(y * 0.4)
    for _ in range(N * N // 8):                      # a scattering of defects
        t[rng.randrange(N)][rng.randrange(N)] = rng.uniform(0.0, 1.0)
    return t

def denoise(field, rounds=SMOOTH):
    """Local smoothing. The surrogate for a diffusion denoiser: cheap, and it is honest
    about what it is -- a low-pass filter, which is what makes it able to smooth away
    defects without knowing where they are."""
    f = [row[:] for row in field]
    for _ in range(rounds):
        nxt = [row[:] for row in f]
        for y in range(N):
            for x in range(N):
                acc, cnt = 0.0, 0
                for dy, dx in ((0,0),(0,1),(0,-1),(1,0),(-1,0)):
                    yy, xx = y+dy, x+dx
                    if 0 <= yy < N and 0 <= xx < N:
                        acc += f[yy][xx]; cnt += 1
                nxt[y][x] = acc / cnt
        f = nxt
    return f

def err(field, t):
    return sum(abs(field[y][x] - t[y][x]) for y in range(N) for x in range(N)) / (N*N)

def noisy(field, t):
    """A LOCAL, cheap proxy: how far is this cell from its own neighbours' mean? A diffusion
    denoiser will have smoothed away anything that stands out, so a residual defect has to be
    judged some other way -- which is precisely why a learned judge is being proposed."""
    out = []
    for y in range(N):
        row = []
        for x in range(N):
            nb = [field[y+dy][x+dx] for dy, dx in ((0,1),(0,-1),(1,0),(-1,0))
                  if 0 <= y+dy < N and 0 <= x+dx < N]
            row.append(abs(field[y][x] - sum(nb)/len(nb)))
        out.append(row)
    return out

def ask_judge(field, t, y, x):
    st = (f"Scene target at this coordinate is {t[y][x]:.2f}. "
          f"The render currently shows {field[y][x]:.2f}. "
          f"Its four neighbours show: "
          f"{', '.join(f'{field[y+dy][x+dx]:.2f}' for dy,dx in ((0,1),(0,-1),(1,0),(-1,0)) if 0 <= y+dy < N and 0 <= x+dx < N)}.")
    r = judge(st, CRIT, "Does this cell already match what the scene calls for, or does it need correcting?")
    return r

import math

_JUDGE_CACHE = {}

def judge_ranking(seed):
    """Score every cell ONCE per seed, then reuse the ranking for every budget.

    Asking the judge per (seed, budget, cell) would be 5 x 7 x 144 = 5040 calls for one
    table. The ranking does not depend on the budget -- only on the denoised field -- so
    the honest and affordable thing is to ask once and reuse. The alternative, shrinking
    the problem to make it cheap, would change what is being measured.
    """
    if seed in _JUDGE_CACHE:
        return _JUDGE_CACHE[seed]
    rng = random.Random(seed)
    t = target(rng)
    start = [[rng.uniform(0, 1) for _ in range(N)] for _ in range(N)]
    f = denoise(start)
    scored = []
    for y in range(N):
        for x in range(N):
            r = ask_judge(f, t, y, x)
            scored.append((r.get("p", 0.0), (y, x)))
            time.sleep(0.06)
    scored.sort(reverse=True)
    _JUDGE_CACHE[seed] = (scored, t, f)
    return _JUDGE_CACHE[seed]

def run_judge(seed, budget):
    scored, t, f = judge_ranking(seed)
    ff = [row[:] for row in f]
    for _, (y, x) in scored[:budget]:
        ff[y][x] = t[y][x]
    return err(ff, t)

def run(seed, budget, selector, use_judge=True):
    rng = random.Random(seed)
    t = target(rng)
    start = [[rng.uniform(0, 1) for _ in range(N)] for _ in range(N)]
    f = denoise(start)
    if budget == 0:
        return err(f, t)
    cells = [(y, x) for y in range(N) for x in range(N)]
    if selector == "oracle":
        cells.sort(key=lambda c: -abs(f[c[0]][c[1]] - t[c[0]][c[1]]))
        pick = cells[:budget]
    elif selector == "random":
        rng.shuffle(cells); pick = cells[:budget]
    elif selector == "worst_noise":
        nz = noisy(f, t)
        cells.sort(key=lambda c: -nz[c[0]][c[1]])
        pick = cells[:budget]

    for (y, x) in pick:
        f[y][x] = t[y][x]
    return err(f, t)

if __name__ == "__main__":
    import math
    print("  verifying the judge first\n")
    ok, _ = self_check(verbose=False)
    if not ok:
        print("  JUDGE UNVERLIABLE -- refusing to run"); raise SystemExit(1)
    print("  judge verified 5/5; running the selection experiment\n")
    print("  10x10 field, 12 smoothing passes, correction budget varied, 2 seeds")
    print(f"\n  {'budget':>7} " + "".join(f"{s:>11}" for s in
          ["oracle", "judge", "worst-noise", "random"]))
    table = {}
    for b in BUDGETS:
        row = []
        for sel in ("oracle", "judge", "worst_noise", "random"):
            vals = [run_judge(s, b) if sel == "judge" else run(s, b, sel) for s in SEEDS]
            row.append(st.mean(vals))
        table[b] = {s: round(v, 4) for s, v in zip(("oracle","judge","worst_noise","random"), row)}
        print(f"  {b:>7} " + "".join(f"{v:>11.4f}" for v in row))
    bmax = BUDGETS[-1]
    o, j, w, r = (table[bmax][k] for k in ("oracle","judge","worst_noise","random"))
    print(f"""
  READING IT
  -----------
  At budget {bmax} (out of {N*N} cells):
    oracle      {o:.4f}
    judge       {j:.4f}   ({100*(j-o)/max(o,1e-9):+.0f}% from the ceiling)
    worst-noise {w:.4f}
    random      {r:.4f}

  The number that matters is the gap between JUDGE and ORACLE, not between JUDGE and
  RANDOM. Beating random only shows there is a signal. Beating random by a lot less than
  the oracle would mean the signal is real but weak, and the paradigm would work in
  principle and disappoint in practice.
""")
    json.dump(table, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       "exp4_results.json"), "w"), indent=1)
    print("  -> exp4_results.json")
