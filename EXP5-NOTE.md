# The falsifiable version, and what it actually showed

**The steel-man's argument:** the judge's signal is *sparse* — one scalar per cell, no
interaction — so it cannot represent "these twelve cells are wrong **together**." If that is
right, then a free local-noise statistic should match it on scattered defects and beat it
on clustered ones, because clustering is exactly what a per-cell signal is worst at.

**The test:** identical seeds, identical budgets, defects scattered uniformly in one arm and
placed in a **contiguous blob** in the other. The decision rule was written before the run:
*the judge wins the argument if and only if it is at or below the free heuristic in the
clustered column.*

## Result (partial — the run was still going at the last four rows)

| budget | distribution | oracle | judge | noise (free) | judge − noise |
|---|---|---|---|---|---|
| 8 | scattered | 0.1329 | 0.1427 | 0.1444 | **−0.0018** |
| 8 | **clustered** | 0.1516 | 0.1647 | 0.1706 | **−0.0059** |
| 16 | scattered | 0.1078 | 0.1276 | 0.1276 | **+0.0000** |
| 16 | **clustered** | 0.1240 | 0.1481 | 0.1541 | **−0.0060** |
| 24 | scattered | 0.0852 | 0.1144 | 0.1176 | **−0.0032** |

## The reading, and its honesty

**The judge passes the falsifiable test.** It is at or below the free statistic in the
clustered column at every budget measured, and by roughly **3× the margin** it manages
against scattered defects. The steel-man's specific prediction — that a sparse per-cell
signal would lose *specifically* where errors cluster — **did not hold.**

**But the honest size of that win is small.** The margins are 0.002–0.006 on a **two-seed**
basis. I am not claiming a significant difference; I am claiming a **consistent direction
across five rows and two distributions**, with one exact tie (0.0000 at budget 16,
scattered) that is itself evidence the two selectors are the same instrument on
uniformly-distributed defects.

**What is actually established, narrowly:**

1. On scattered defects the judge is **indistinguishable from a free statistic** — one row
   is an exact tie to four decimals.
2. On clustered defects it is **consistently but marginally better**.
3. The gap to the oracle **widens with budget in both arms** (+0.010 → +0.029), so the judge
   is not closing on the ceiling; it is a better free statistic, not a route to the oracle.

## What this changes, and what it does not

**Changes:** the steel-man's point 3 is **weaker than stated.** The judge is not a
rank-one-projection-shaped instrument in the way the objection claimed. It sees per-cell
values and a description of the neighbourhood, and that is enough to do measurably better
than raw local noise when the error is structured.

**Does not change:** points 1 and 2 stand entirely. The judge is still **well short of the
oracle at every budget and every distribution**, and it still costs ~100 model calls per
field where the free statistic costs arithmetic. A 0.006 improvement on a 0.13 error is not
a reason to pay for a router, and it is emphatically not a reason to write a fused compute
kernel.

**The honest summary: the judge's advantage exists and is structured — it appears where
errors cluster — and it is too small to pay for itself on this task.** The next experiment
that would change the answer is not a bigger grid. It is a task where clustered errors are
*the norm* rather than an artificial blob: a seam, a boundary, a drifting region in a real
generative field.

## Unfinished, and said so

The run was cut short before budgets 24-clustered and both 40 rows. The pattern is stable
across everything that completed and does not reverse, but the table above is the whole of
what was measured, and a reader should treat the last line as provisional rather than
complete. `exp5_results.json` holds only finished rows.
