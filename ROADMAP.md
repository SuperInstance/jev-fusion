# Roadmap

Ordered by what unblocks the most, and worked in parallel wherever the dependencies allow.
Every item names its control, because a control that cannot fail is the most expensive thing
we own.

## Lane A — the judge as an instrument (IN FLIGHT, blocks most of the rest)

The four proposed fusions all assume a fast discrete judge is worth its call. One experiment
says it is not — indistinguishable from a free local-noise heuristic, 56% off the oracle
ceiling. **Everything downstream depends on whether that survives.**

- **A1. Give the judge the latent, not a caption.** It currently sees four numbers. A real
  System-1 reader sees a representation. If the gap to oracle does not close, the paradigm is
  dead and we saved ourselves the GPU. *Control: the same cells judged from a shuffled
  neighbour assignment.*
- **A1b. CLUSTERED vs SCATTERED — DONE (`EXP5-NOTE.md`).** The steel-man predicted a sparse
  per-cell signal would lose *specifically* where errors cluster. **It did not.** The judge
  is at or below the free statistic in the clustered column at every budget measured, by ~3x
  the margin it manages on scattered — where one row is an *exact* tie. Narrow, and on a
  two-seed basis, and stated as such.
- **A1c. THE SEAM TASK — IN FLIGHT (`exp6_seam_task.py`).** The experiment that would settle
  whether A1b matters in reality. Clustered error as a *mirrored seam* rather than an
  artificial blob: both sides are wrong in the same direction, so neither disagrees with its
  own neighbours and the corruption is visible only by comparing LEFT to RIGHT. The control is
  the same strip corrupted *randomly*, which preserves the amount of noise and destroys the
  cross-seam signal. **Win on seam only = the judge reads cross-seam structure. Win on both =
  it is reading the amount of corruption and the seam framing is decoration.**
- **A2. Measure the crossover.** At what budget does the judge overtake free heuristics? If
  never, stop. *Control: sweep budget to the point where oracle saturates.*
- **A3. Is there a task where the judge wins big?** It may be excellent at coarse routing and
  useless at fine selection. Coarse/fine split, measured separately.

## Lane B — the generative field (IN FLIGHT, no dependency on Lane A)

The d+1 law holds in 2-D and 3-D on one local rule. It is the most robust finding we have and
it does not depend on any model.

- **B1. Scale to 4-D and 5-D.** Does it keep holding d+1? Or is 3 special?
- **B2. Boundary stability in 2-D.** The 1-D boundary dissolved under perturbation; the 2-D
  one survived. Confirm at 3-D, where the boundary is a surface. *Control: the annealing
  test that killed 1-D.*
- **B3. Does the tissue count track dimension or neighbourhood size?** k and d are
  confounded in every run so far. Separate them.
- **B4. Why a dimension changes the stability class.** The open mechanism question. Plausible:
  a boundary can be a real barrier in the plane and must always leak along a line. Untested.

## Lane C — self-decomposition (IN FLIGHT)

The gate reads membership correctly and is biased toward safety. The rebalance failed, which
tells us the bias is the signal and not a prior.

- **C1. Better evidence, not a better prior.** Give the judge the *history* of what it has
  compiled rather than a one-sentence class description.
- **C2. Asymmetric costs in the question itself.** Ask "is it safer to call the model or run
  the compiled path" rather than asking for a category and hoping a threshold lands right.
- **C3. Closed-loop compilation.** Compile, watch the error rate, uncompile what drifts. The
  loop nobody has proposed, because it is the one that has to be right.

## Lane D — the encodings (IN FLIGHT, cheap and already paying)

- **D1. Alignment is the dial, not count.** Already established. Now: is there an alignment
  that is robust for *every* plausible material set, or only for the one we tested?
- **D2. The 2×4 pool floor.** A ladder finer than the pool's quantisation is spend without
  information. What is the actual floor?
- **D3. A vision model reading the text.** Blocked on `mcode-tools` credentials. This is the
  experiment that would settle "agentic vision" rather than "can a linear policy".

## Sequencing

**A1 gates the most.** If the judge cannot close the gap, three of the four proposed
architectures are not worth building and Lane A should shrink rather than grow.

**B runs free** and is the only lane whose findings need no model at all, so it is the right
place to put effort that would otherwise be blocked.

**C is cheap to keep alive and expensive to abandon**, because the gate's bias is in the safe
direction and safe-but-slow is still a working system.

**D is already producing answers** and costs one API call per experiment.

## What is deliberately NOT on this list

- Writing a custom compute shader. Until A1 says the judgement is worth fusing, a fused
  projection is a way of paying VRAM for something we have not shown is worth anything.
- Live weight edits during sampling. Test-time adaptation is a real literature with known
  instability, and we should read it before we write it.
- A vision-language evaluation, while the multimodal lane is blocked on credentials.
