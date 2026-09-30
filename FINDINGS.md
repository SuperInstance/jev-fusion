# Findings

## The judge is verified before anything is believed

An earlier piece of this work concluded that the discrete judge "does not discriminate," and
published it. That was a **malformed request**, not a property of the model: `state` was an
object rather than a string, and a separate `options` list was sent alongside `criteria`. There
is no `options` field — the option set IS the criteria keys. A malformed spec does not error; it
returns a well-formed, confidently unhelpful answer.

`jev_check.py` re-verifies 5/5 before every experiment, and an experiment refuses to run if the
check fails. **A negative control that shares the call path of the thing it audits cannot
detect a fault in that path.**

## Claim 4 — selective refinement: the premise holds, the judge does not earn its cost

The testable content of "spend compute only where a fast judge flags" is a **selection**
problem, not an image-quality problem. Given a fixed correction budget, is the judge's flag
better than the alternatives? That needs no GPU and it is the whole method.

A 10×10 field is denoised by local smoothing toward a known target, scattered with defects.
Correcting a cell costs one unit of budget. Four selectors, same budget:

| budget | oracle | judge | worst-noise (free) | random |
|---|---|---|---|---|
| 4 | 0.1472 | 0.1538 | **0.1533** | 0.1582 |
| 8 | 0.1329 | 0.1425 | 0.1444 | 0.1514 |
| 16 | 0.1078 | 0.1278 | **0.1276** | 0.1364 |
| 24 | 0.0852 | 0.1132 | 0.1176 | 0.1225 |
| 40 | 0.0496 | 0.0773 | 0.0899 | 0.0944 |

**THE JUDGE IS NOT DISTINGUISHABLE FROM A FREE LOCAL-NOISE HEURISTIC.** At budget 4 the free
statistic is *better* (0.1533 vs 0.1538); at 16 they tie to four decimals. The judge pulls
ahead only at high budget (0.0773 vs 0.0899), and even there it is **56% worse than the
oracle ceiling**.

**The honest verdict, stated against the claim's own framing:**

- **The premise is sound.** Selective spending beats uniform spending. Judge beats random at
  every budget, by ~5% at low budget and ~18% at high budget. There is a real signal.
- **The instrument does not earn its cost.** It does the same job as a statistic you can
  compute for free from the field itself, on the fields tested here, at roughly 100 model
  calls per field. The compute spent judging would buy more smoothing.

**What this does not settle.** The judge sees a *description* of a cell — its value, its
neighbours' values, and the target. It does not see the true error. A real System 1 model in
this loop would see the *latent*, not a caption of four numbers. So this is evidence against
the obvious implementation, not against the idea in general. The sharp next test gives the
judge the same information a latent-reading judge would have and asks whether the gap to
oracle closes.

**The number an implementer wants** is the judge-to-oracle gap, and it is currently 56% at
budget 40. A cascade is worth building when that gap is small. It is not small here.
