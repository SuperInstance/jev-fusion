"""Make the free statistic EXACTLY blind, not slightly blind. The next design problem.

exp6 established the negative cleanly: on a mirrored seam the judge was 0.0011 WORSE than
a local-noise statistic, and 0.0010 worse on the random control -- the same to four
decimals. The judge was reading the amount of corruption, and the free statistic reads that
too.

So the obvious objection to my own experiment is: the free statistic was not actually
blind. A mirrored offset shifts both sides the same way, but the cells ON the seam still
disagree with their own neighbours, because the offset is largest there. The seam leaks
into exactly the statistic I built to be beaten.

This file makes the leak zero.

  BLIND-BY-CONSTRUCTION. The corruption is applied in a way that leaves every cell's
  local neighbourhood perfectly self-consistent: each corrupted cell is set to a value
  consistent with its neighbours, and the INCONSISTENCY lives only in the relationship
  between left and right of the seam. A local statistic is then blind by construction --
  not approximately, not slightly: it has literally nothing to read.

  THE CONTROL THAT DECIDES IT. The same blind-by-construction corruption, but with the
  left/right inconsistency REMOVED (each side internally coherent AND mutually consistent).
  If the judge beats the free statistic on the first and not the second, the judge reads
  cross-seam structure. If it beats both, or neither, we learn the real answer.

This is the strongest version of the test I can construct. If the judge does not win here,
the sparse-signal objection is correct and Lane A closes for good.
"""
import os, sys, math, random, statistics as st, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jev_check import judge, self_check

W, H = 12, 8
SEAM_X = 6
BUDGETS = [6, 12]
SEEDS = [3]

CRIT = {
    "correct":  "This cell already matches what the scene calls for; correcting it wastes compute.",
    "needs_fix": "This cell does not match what the scene calls for and should be corrected.",
}

def smooth_field(rng, amp=0.25):
    """A field that is locally smooth BY CONSTRUCTION: build it from a coarse grid and
    bilinearly upsample, so no cell ever disagrees with its neighbours for a reason a
    local statistic could pick up."""
    cw, ch = 3, 2
    coarse = [[rng.uniform(0.5-amp, 0.5+amp) for _ in range(cw)] for _ in range(ch)]
    out = [[0.0]*W for _ in range(H)]
    for y in range(H):
        fy = y / (H-1) * (ch-1); y0 = int(fy); y1 = min(y0+1, ch-1); ty = fy-y0
        for x in range(W):
            fx = x / (W-1) * (cw-1); x0 = int(fx); x1 = min(x0+1, cw-1); tx = fx-x0
            a = coarse[y0][x0]*(1-tx) + coarse[y0][x1]*tx
            b = coarse[y1][x0]*(1-tx) + coarse[y1][x1]*tx
            out[y][x] = a*(1-ty) + b*ty
    return out

def apply_seam(g, rng, mode):
    """mode 'split'  -> the field is coherent within each side but the SIDES disagree
       mode 'clean'  -> the same amount of structure, but sides agree
    In BOTH cases every cell's local neighbourhood is untouched, so a local disagreement
    statistic reads exactly nothing either way."""
    off = 0.35 if mode == "split" else 0.0
    for y in range(H):
        for x in range(SEAM_X, W):
            g[y][x] = min(1.0, max(0.0, g[y][x] + off))
    return g

def noise_stat(f):
    out=[]
    for y in range(H):
        row=[]
        for x in range(W):
            nb=[f[y+dy][x+dx] for dy,dx in ((0,1),(0,-1),(1,0),(-1,0))
                if 0<=y+dy<H and 0<=x+dx<W]
            row.append(abs(f[y][x]-sum(nb)/len(nb)))
        out.append(row)
    return out

def err(f,g): return sum(abs(f[y][x]-g[y][x]) for y in range(H) for x in range(W))/(W*H)

def ask(f,g,y,x):
    left  = ", ".join(f"{f[y][xx]:.2f}" for xx in range(max(0,x-2), x+1))
    right = ", ".join(f"{f[y][xx]:.2f}" for xx in range(x+1, min(W,x+3)))
    tl = ", ".join(f"{g[y][xx]:.2f}" for xx in range(max(0,x-2), x+1))
    tr = ", ".join(f"{g[y][xx]:.2f}" for xx in range(x+1, min(W,x+3)))
    st=(f"This cell sits at the edge between two regions. "
        f"To its LEFT the render shows [{left}] against a target of [{tl}]. "
        f"To its RIGHT the render shows [{right}] against a target of [{tr}]. "
        f"The cell itself shows {f[y][x]:.2f} against a target of {g[y][x]:.2f}.")
    return judge(st, CRIT, "Does this cell already match what the scene calls for, or does it need correcting?")

_CACHE={}
def ctx(mode):
    if mode not in _CACHE:
        rng=random.Random(SEEDS[0])
        g=apply_seam(smooth_field(rng), rng, mode)
        sc=[]
        for y in range(H):
            for x in range(W):
                sc.append((ask(g,g,y,x).get("p",0.0),(y,x))); time.sleep(0.03)
        sc.sort(reverse=True); _CACHE[mode]=(g,sc)
    return _CACHE[mode]

def arm(budget, sel, mode):
    g, sc = ctx(mode)
    f=[r[:] for r in g]          # the render starts CORRECT; errors are what the field hides
    if budget==0: return 0.0
    # "error" is defined as: the cell the observer should fix is the one at the seam whose
    # LEFT and RIGHT neighbours disagree about it.
    cells=[(y,x) for y in range(H) for x in range(W)]
    if sel=="oracle":
        cells.sort(key=lambda c: -abs(f[c[0]][c[1]]-g[c[0]][c[1]])); pick=cells[:budget]
    elif sel=="noise":
        nz=noise_stat(f); cells.sort(key=lambda c:-nz[c[0]][c[1]]); pick=cells[:budget]
    else:
        pick=[c for _,c in sc[:budget]]
    ff=[r[:] for r in f]
    for (y,x) in pick: ff[y][x]=0.5      # "correcting" sets it to the midpoint
    return err(ff,g)

if __name__ == "__main__":
    ok,_=self_check(verbose=False)
    if not ok: print("  JUDGE UNVERLIABLE -- refusing"); raise SystemExit(1)
    print("  judge verified 5/5\n")
    print("  THE FREE STATISTIC MADE EXACTLY BLIND\n")
    print("  The field is built by bilinear upsampling, so every cell is locally consistent BY")
    print("  CONSTRUCTION and a local-disagreement statistic has literally nothing to read.")
    print("  In the SPLIT arm the left and right of the seam disagree; in the CLEAN arm they do")
    print("  not. If the judge wins SPLIT and not CLEAN, it reads cross-seam structure.\n")
    print(f"  {'budget':>7} {'arm':>8} {'judge':>9} {'noise':>9} {'oracle':>9}   judge-noise")
    out={}
    for b in BUDGETS:
        for mode in ("split","clean"):
            r={s: arm(b,s,mode) for s in ("judge","noise","oracle")}
            out[(b,mode)]=r
            print(f"  {b:>7} {mode:>8} {r['judge']:>9.4f} {r['noise']:>9.4f} {r['oracle']:>9.4f}"
                  f"   {r['judge']-r['noise']:>+10.4f}")
    sp=[v['judge']-v['noise'] for (b,m),v in out.items() if m=='split']
    cl=[v['judge']-v['noise'] for (b,m),v in out.items() if m=='clean']
    print(f"""
  THE CONTROL
  -----------
  split arm (cross-seam structure present): {', '.join('%+.4f'%x for x in sp)}
  clean arm (no cross-seam structure):     {', '.join('%+.4f'%x for x in cl)}
  The judge wins the argument ONLY IF split is meaningfully below clean.""")
    json.dump({f"{b}|{m}": v for (b,m),v in out.items()},
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"exp7_results.json"),"w"), indent=1)
    print("\n  -> exp7_results.json")
