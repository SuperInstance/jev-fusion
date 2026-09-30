"""The steel-man's falsifiable version: does the judge win where the errors CLUSTER?

exp4 scattered defects uniformly. That is the single distribution most favourable to a
free per-cell statistic and least favourable to a per-cell judge, because a uniform field
gives the free statistic the same thing it always has: local disagreement with neighbours.

The steel-man's own argument says the judge's signal is SPARSE -- one scalar per cell, no
interaction -- and therefore cannot represent "these twelve cells are wrong TOGETHER." A
boundary, a seam, and a contiguous misassigned region are all exactly that: errors that
arrive as a group.

So: re-run the selector with the defects placed in a CONTIGUOUS BLOB rather than
scattered, and see whether the judge overtakes the free heuristic.

  THIS IS THE FALSIFIABLE VERSION. If the judge still does not overtake, the steel-man
  wins and Lane A closes. If it does, the judge is good at precisely one thing and we
  build only that thing.

THE CONTROL THAT DECIDES IT: at equal budget, compare
  judge vs worst-noise (the free statistic) vs oracle (the ceiling)
on both defect distributions, run side by side, same seeds. If the judge's advantage
exists at all, it must appear in the CLUSTERED column and not the SCATTERED one. An
advantage that is present in both is not about clustering and we should say so.
"""
import os, sys, math, random, statistics as st, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jev_check import judge, self_check

N = 10
SMOOTH = 12
BUDGETS = [8, 16, 24, 40]
SEEDS = [3, 7]

CRIT = {
    "correct":  "This cell already matches what the scene calls for; correcting it wastes compute.",
    "needs_fix": "This cell does not match what the scene calls for and should be corrected.",
}

def target(rng, defects, clustered):
    t = [[0.0]*N for _ in range(N)]
    for y in range(N):
        for x in range(N):
            t[y][x] = 0.5 + 0.35*math.sin(x*0.5)*math.cos(y*0.4)
    if clustered:
        # ONE contiguous blob, the shape a seam or a tissue boundary would make
        cy, cx, r = N//2, N//2, 2
        for y in range(max(0,cy-r), min(N,cy+r+1)):
            for x in range(max(0,cx-r), min(N,cx+r+1)):
                if (y-cy)**2 + (x-cx)**2 <= r*r:
                    t[y][x] = rng.uniform(0.0, 1.0)
    else:
        for _ in range(defects):
            t[rng.randrange(N)][rng.randrange(N)] = rng.uniform(0.0, 1.0)
    return t

def denoise(f, rounds=SMOOTH):
    f=[r[:] for r in f]
    for _ in range(rounds):
        nxt=[r[:] for r in f]
        for y in range(N):
            for x in range(N):
                acc=cnt=0
                for dy,dx in ((0,0),(0,1),(0,-1),(1,0),(-1,0)):
                    yy,xx=y+dy,x+dx
                    if 0<=yy<N and 0<=xx<N: acc+=f[yy][xx]; cnt+=1
                nxt[y][x]=acc/cnt
        f=nxt
    return f

def err(f,t): return sum(abs(f[y][x]-t[y][x]) for y in range(N) for x in range(N))/(N*N)

def noisy(f):
    out=[]
    for y in range(N):
        row=[]
        for x in range(N):
            nb=[f[y+dy][x+dx] for dy,dx in ((0,1),(0,-1),(1,0),(-1,0))
                if 0<=y+dy<N and 0<=x+dx<N]
            row.append(abs(f[y][x]-sum(nb)/len(nb)))
        out.append(row)
    return out

def ask(f,t,y,x):
    st=(f"Scene target at this coordinate is {t[y][x]:.2f}. The render currently shows "
        f"{f[y][x]:.2f}. Its four neighbours show: "
        f"{', '.join(f'{f[y+dy][x+dx]:.2f}' for dy,dx in ((0,1),(0,-1),(1,0),(-1,0)) if 0<=y+dy<N and 0<=x+dx<N)}.")
    return judge(st, CRIT, "Does this cell already match what the scene calls for, or does it need correcting?")

def arm(seed, budget, selector, clustered):
    rng=random.Random(seed)
    t=target(rng, N*N//8, clustered)
    f=denoise([[rng.uniform(0,1) for _ in range(N)] for _ in range(N)])
    if budget==0: return err(f,t)
    cells=[(y,x) for y in range(N) for x in range(N)]
    if selector=="oracle":
        cells.sort(key=lambda c: -abs(f[c[0]][c[1]]-t[c[0]][c[1]])); pick=cells[:budget]
    elif selector=="noise":
        nz=noisy(f); cells.sort(key=lambda c:-nz[c[0]][c[1]]); pick=cells[:budget]
    else:
        sc=[]
        for (y,x) in cells:
            sc.append((ask(f,t,y,x).get("p",0.0),(y,x))); time.sleep(0.05)
        sc.sort(reverse=True); pick=[c for _,c in sc[:budget]]
    ff=[r[:] for r in f]
    for (y,x) in pick: ff[y][x]=t[y][x]
    return err(ff,t)

if __name__ == "__main__":
    ok,_=self_check(verbose=False)
    if not ok: print("  JUDGE UNVERLIABLE -- refusing"); raise SystemExit(1)
    print("  judge verified 5/5\n")
    print("  THE FALSIFIABLE VERSION: clustered defects vs scattered\n")
    print(f"  {'budget':>7} {'dist':>10} {'oracle':>9} {'judge':>9} {'noise':>9}   judge-oracle   judge-noise")
    out={}
    for b in BUDGETS:
        for clustered, name in ((False,"scattered"),(True,"clustered")):
            r={s: st.mean([arm(sd,b,s,clustered) for sd in SEEDS]) for s in ("oracle","judge","noise")}
            out[(b,name)]=r
            flag = "  <-- JUDGE WINS" if r["judge"]<r["noise"] else ""
            print(f"  {b:>7} {name:>10} {r['oracle']:>9.4f} {r['judge']:>9.4f} {r['noise']:>9.4f}"
                  f"   {r['judge']-r['oracle']:>+11.4f}   {r['judge']-r['noise']:>+10.4f}{flag}")
    sc_j=out[(40,"scattered")]; cl_j=out[(40,"clustered")]
    print(f"""
  THE VERDICT
  -----------
  At the largest budget, judge vs the free statistic:
    scattered defects   judge {sc_j['judge']:.4f}  noise {sc_j['noise']:.4f}   -> {sc_j['judge']-sc_j['noise']:+.4f}
    clustered defects   judge {cl_j['judge']:.4f}  noise {cl_j['noise']:.4f}   -> {cl_j['judge']-cl_j['noise']:+.4f}

  THE DECISION RULE, stated before the numbers: the judge wins the argument if and only if
  it is at or below the free heuristic in the CLUSTERED column. An advantage present in
  both columns is not about clustering and does not support the sparse-signal objection
  being wrong.""")
    json.dump({f"{b}|{n}": v for (b,n),v in out.items()},
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"exp5_results.json"),"w"), indent=1)
    print("\n  -> exp5_results.json")
