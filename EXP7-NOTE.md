# The free statistic made exactly blind — and it still doesn't matter

## What this was built to do

exp6 left one objection standing, and it was an objection to *my experiment*, not to the
judge. A mirrored seam shifts both sides the same way, but the cells **on** the seam still
disagree with their own neighbours, because the offset is largest there. So the "free"
statistic was not actually blind — it was reading the leak, and beating it proved less than
I wanted it to.

The fix: build the field by **bilinear upsampling from a coarse grid**, so every cell is
locally consistent *by construction* and a local-disagreement statistic has literally
nothing to read. Not approximately blind. Blind.

Then the arm that decides it:

- **SPLIT** — left and right of the seam disagree. Cross-seam structure is present.
- **CLEAN** — the same field, no split. Nothing structural to find.

**The judge wins the argument only if SPLIT is meaningfully below CLEAN.**

## Result

| budget | arm | oracle | judge | noise | judge − noise |
|---|---|---|---|---|---|
| 6 | split | 0.0040 | 0.0089 | 0.0165 | **−0.0076** |
| 6 | clean | 0.0040 | 0.0036 | 0.0096 | **−0.0060** |
| 12 | split | 0.0243 | 0.0232 | 0.0325 | **−0.0093** |
| 12 | clean | 0.0059 | 0.0071 | 0.0153 | **−0.0082** |

**The control fired. The judge wins by essentially the same amount on both arms.**

Split: −0.0076, −0.0093. Clean: −0.0060, −0.0082. The difference between "there is
cross-seam structure here" and "there is not" is smaller than the margin the judge already
had.

## What the judge's advantage actually is

**Not cross-seam structure. A general advantage on smooth fields.**

On a locally coherent field the question is "which cells should I move toward the midpoint",
and the judge is a better answer than local-noise-ranked cells — by ~0.007, whether or not
anything structural is present. That is a real advantage and it is much more modest than the
one I was hoping for.

It is also **not close to the ceiling**: at budget 6 the oracle is 0.0040 and the judge
0.0089, so the judge is still more than twice the oracle's error. And note the judge is
*worse* than the oracle in the clean arm (0.0071 vs 0.0059) while the noise statistic is far
worse in both — the free statistic's failure is uniform, the judge's is not.

## The conclusion, and it is a real one

**Lane A closes.** Three designed experiments, three controls, three negatives:

| | distribution | judge vs free |
|---|---|---|
| exp4 | scattered defects | indistinguishable — one row an exact tie |
| exp5 | inserted contiguous blob | judge better by ~0.006 |
| exp6 | mirrored seam | free better by ~0.001, on both arms |
| **exp7** | **free statistic exactly blind** | **judge better by ~0.007 — on BOTH arms** |

The judge has a small, real, general advantage on smooth fields. It has **no advantage
attributable to reading structure across cells**, and that was the only version of the claim
that would have justified building a router, a fused kernel, or an external-model-as-router
design. exp7 is the strongest test I could construct, and it is the one that settles it:
**when the free statistic was made literally blind, the judge's edge did not change.**

I am closing the lane rather than reframing it. The honest result is worth more than a
weaker version of the same claim.

## What survives, and where it could still matter

1. **A ~0.007 advantage over a free statistic, on smooth fields, at 100 model calls per
   field.** That is a bad trade at this margin. It would need to be 5–10× larger, or the
   calls would need to be an order of magnitude cheaper, to be worth a router.
2. **The measurement apparatus is the real output.** A control that can be made blind, and
   then is, is the reusable thing. Three of tonight's experiments were decided by their
   controls rather than by their numbers.
3. **The open question moves rather than closes.** If per-cell selection is genuinely
   capped, the interesting direction is not a better *selector* but a representation where
   the cross-cell structure is carried in the *observation* rather than reconstructed by a
   judge. That is an encoding question, not a routing one — and it is where Lane D already
   has a provable result.
