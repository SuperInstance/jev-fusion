"""The task where clustered error is the NORM, not an artificial blob.

exp5 put the defects in a contiguous blob and the judge beat the free statistic by
~0.006. Small, and on an artificial distribution. A blob dropped into a uniform field is
a thing I made, and the question is whether anything real looks like that.

It does, and the literature says so: in multi-canvas diffusion, the failure mode is
specifically a **seam** -- a narrow strip where two separately-generated regions disagree.
SyncDiffusion's finding is that naive blending is "seamless but incoherent." The defect
is not scattered and not a blob. It is a **thin band with a known orientation**, and the
question is whether a judge can find it better than local noise.

THE TASK. Two regions are generated separately, each from its own smooth process. Along a
vertical seam, a strip of cells is corrupted -- and corrupted in a way that a per-cell
neighbour-disagreement statistic cannot see, because BOTH sides of the seam disagree with
their own neighbours symmetrically. The seam is only visible by comparing LEFT to RIGHT.

  P0  the seam, as described
  P1  a control: the same strip corrupted, but with the disagreement on both sides RANDOM
      rather than mirrored, which destroys the "compare across the seam" signal while
      preserving the amount of local noise

If the judge beats local noise on P0 and does NOT on P1, then it is reading cross-seam
structure, which is exactly the thing a per-cell free statistic cannot do and the thing a
seam in a real generative field always has.

If it beats the free statistic on BOTH, then it is not reading the seam; it is reading the
*amount* of corruption, which any reasonable statistic can also read, and the seam
framing is decoration.

That control is the whole experiment. A win on P0 alone is the interesting result.
"""
import os, sys, math, random, statistics as st, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jev_check import judge, self_check

W, H = 20, 12
SEAM_X = 10
BUDGETS = [6, 12, 20]
SEEDS = [3, 7, 11]

CRIT = {
    "correct":  "This cell already matches what the scene calls for; correcting it wastes compute.",
    "needs_fix": "This cell does not match what the scene calls for and should be corrected.",
}

def scene(rng, mode):
    """mode: 'seam' (mirrored disagreement) or 'random' (uncorrelated corruption)."""
    g = [[0.5 + 0.3*math.sin(x*0.4) + 0.3*math.cos(y*0.5) for x in range(W)] for y in range(H)]
    if mode == "seam":
        # mirror the error across the seam: both sides are wrong in the SAME direction,
        # so neither side disagrees with its own neighbours -- only across does.
        off = rng.uniform(-0.35, 0.35)
        for y in range(H):
            for d in (1, 2):
                for x in (SEAM_X - d, SEAM_X + d - 1):
                    if 0 <= x < W:
                        g[y][x] = min(1.0, max(0.0, g[y][x] + off * (1.0 - 0.2*d)))
    else:
        for y in range(H):
            for d in (1, 2):
                for x in (SEAM_X - d, SEAM_X + d - 1):
                    if 0 <= x < W:
                        g[y][x] = min(1.0, max(0.0, g[y][x] + rng.uniform(-.35, .35)))
    return g

def denoise(g, rounds=8):
    f=[r[:] for r in g]
    for _ in range(rounds):
        nxt=[r[:] for r in f]
        for y in range(H):
            for x in range(W):
                s=n=0
                for dy,dx in ((0,0),(0,1),(0,-1),(1,0),(-1,0)):
                    yy,xx=y+dy,x+dx
                    if 0<=yy<H and 0<=xx<W: s+=f[yy][xx]; n+=1
                nxt[y][x]=s/n
        f=nxt
    return f

def err(f,g): return sum(abs(f[y][x]-g[y][x]) for y in range(H) for x in range(W))/(W*H)

def noise_stat(f):
    """The free statistic: how far is this cell from its neighbours' mean."""
    out=[]
    for y in range(H):
        row=[]
        for x in range(W):
            nb=[f[y+dy][x+dx] for dy,dx in ((0,1),(0,-1),(1,0),(-1,0))
                if 0<=y+dy<H and 0<=x+dx<W]
            row.append(abs(f[y][x]-sum(nb)/len(nb)))
        out.append(row)
    return out

def ask(f, g, y, x):
    """Give the judge the horizontal neighbours TOO -- a seam is a cross-cell structure
    and a judge that only sees the vertical neighbourhood is being tested on a task it
    cannot see. This is the cheapest honest version of the test."""
    row = ", ".join(f"{f[y][xx]:.2f}" for xx in range(max(0,x-2), min(W,x+3)))
    st=(f"Scene target along this part of the row is "
        f"{', '.join(f'{g[y][xx]:.2f}' for xx in range(max(0,x-2), min(W,x+3)))}. "
        f"The render shows {row} (columns {max(0,x-2)} to {min(W-1,x+2)}). "
        f"This cell is at column {x}.")
    return judge(st, CRIT, "Does this cell already match what the scene calls for, or does it need correcting?")

def arm(seed, budget, sel, mode):
    rng=random.Random(seed)
    g=scene(rng, mode); f=denoise(g)
    if budget==0: return err(f,g)
    cells=[(y,x) for y in range(H) for x in range(W)]
    if sel=="oracle":
        cells.sort(key=lambda c:-abs(f[c[0]][c[1]]-g[c[0]][c[1]])); pick=cells[:budget]
    elif sel=="noise":
        nz=noise_stat(f); cells.sort(key=lambda c:-nz[c[0]][c[1]]); pick=cells[:budget]
    else:
        sc=[]
        for (y,x) in cells:
            sc.append((ask(f,g,y,x).get("p",0.0),(y,x))); time.sleep(0.04)
        sc.sort(reverse=True); pick=[c for _,c in sc[:budget]]
    ff=[r[:] for r in f]
    for (y,x) in pick: ff[y][x]=g[y][x]
    return err(ff,g)

if __name__ == "__main__":
    ok,_=self_check(verbose=False)
    if not ok: print("  JUDGE UNVERLIABLE -- refusing"); raise SystemExit(1)
    print("  judge verified 5/5\n")
    print("  THE SEAM TASK -- clustered error as the NORM, with a mirrored-disagreement control\n")
    print(f"  {'budget':>7} {'scene':>9} {'oracle':>9} {'judge':>9} {'noise':>9}   judge-noise")
    out={}
    for b in BUDGETS:
        for mode in ("seam","random"):
            r={s: st.mean([arm(sd,b,s,mode) for sd in SEEDS]) for s in ("oracle","judge","noise")}
            out[(b,mode)]=r
            print(f"  {b:>7} {mode:>9} {r['oracle']:>9.4f} {r['judge']:>9.4f} {r['noise']:>9.4f}"
                  f"   {r['judge']-r['noise']:>+10.4f}")
    print(f"""
  THE CONTROL, and it is the whole experiment
  -------------------------------------------
  If the judge beats local noise on the SEAM scene and does NOT on the RANDOM scene, it is
  reading cross-seam structure -- which is exactly what a per-cell free statistic cannot do
  and what a real seam always has.

  If it beats the free statistic on BOTH, it is reading the AMOUNT of corruption, any
  reasonable statistic can read that too, and the seam framing is decoration.

  Read the last two rows together. A win on the seam alone is the interesting result; a
  win on both is not.""")
    json.dump({f"{b}|{m}": v for (b,m),v in out.items()},
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"exp6_results.json"),"w"), indent=1)
    print("\n  -> exp6_results.json")
