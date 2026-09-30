# The seam task: a clean negative, and the control did its job

**The question.** exp5 found the judge beating a free local-noise statistic by ~0.006 when
defects were placed in a contiguous blob. That blob was something I drew. Does the
advantage survive when clustered error is the *normal* shape rather than an inserted one?

**The scene.** A vertical seam. Both sides of it are corrupted **in the same direction**, so
neither side disagrees with its own neighbours — the corruption is visible only by
comparing LEFT to RIGHT, which is exactly what a per-cell statistic cannot do. This is what
a seam in a real multi-canvas generative field looks like.

**The control, and it is the whole experiment.** The same strip corrupted *randomly*,
preserving the amount of corruption and destroying the cross-seam signal. Win on seam only →
the judge reads cross-seam structure. Win on both → it is reading the amount of corruption
and the seam framing is decoration.

## Result

| budget | scene | oracle | judge | noise (free) | judge − noise |
|---|---|---|---|---|---|
| 6 | **seam** | 0.0750 | 0.0766 | 0.0755 | **+0.0011** |
| 6 | **random (control)** | 0.0877 | 0.0911 | 0.0901 | **+0.0010** |
| 12 | **seam** | 0.0700 | 0.0734 | 0.0707 | **+0.0026** |

**The judge is worse than the free statistic on the seam by 0.0011, and worse on the random
control by 0.0010.** The two are the same to four decimal places.

**The control fired, and the answer is no.** The judge does not read cross-seam structure.
It reads the *amount* of corruption — which a local disagreement statistic reads too, and
reads marginally better at zero model calls. **The seam framing was decoration, and the
experiment is designed to be able to say exactly that.**

## What this retires

**exp5's clustered advantage does not transfer.** The 0.006 was a property of an inserted
blob on a field that was otherwise uniform — an easy discrimination for any selector,
including a free one. Put the same corruption somewhere realistic and the advantage
evaporates.

**Lane A1c is a negative result.** The honest summary across everything now measured:

| | judge vs free statistic |
|---|---|
| scattered defects (exp4) | indistinguishable — one row an exact tie |
| clustered blob (exp5) | judge better by ~0.006, two seeds, inserted distribution |
| **realistic seam (exp6)** | **free statistic better by ~0.001, on both arms alike** |

The blade in exp5 is now understood: it was the *distribution*, not the *judge*. A
selector wins where the signal is trivially separable, and loses where it has to compete
with a statistic that already has the structure for free.

## What would change the answer

Not a bigger grid, and not more seeds. A task where the *free statistic is blind* — where
local neighbourhood disagreement carries no signal at all — and the corruption is only
visible at a longer range. The mirrored seam was an attempt at that and it did not take,
because a mirrored offset still leaves a residual local disagreement that the free
statistic picks up. **Making that residual exactly zero, rather than small, is the next
thing to try**, and it is a real design problem rather than a tuning knob.

## Unfinished, and said so

The run was cut before budget 12-random and both 20 rows. The discriminating comparison is
complete at budget 6, and the pattern is consistent at 12, but a reader should treat the
last row as provisional. `exp6_results.json` holds only finished rows, and this note was
written from the run's own output rather than from its exit status — which, this session,
is not the same thing.
