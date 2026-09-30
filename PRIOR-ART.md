# Prior art on the four proposed fusions

An adversarial scout reviewed all four architectures against the literature. Its verdict,
before any of my own experiments is weighed:

| # | claim | published? | the name it already has |
|---|---|---|---|
| 1 | fused projection kernel | **yes, mechanism fully** | GLIGEN / T2I-Adapter / Universal Guidance |
| 2 | live weight edits mid-denoising | **yes, with two negative results** | Diffusion-TTA, DiffusionCLIP, TTT fast-weights |
| 3 | multi-canvas + central router | **yes, two literatures** | MultiDiffusion / Mixture-of-Diffusers / SyncDiffusion / MIGC |
| 4 | alternating S1/S2 refinement | **yes, densely** | adaptive computation: DyDiT, AdaDiff, DuoDiff |

**Only one of the four is worth building, and it is #4 — but not for the reason it was
proposed.**

## The one number that should govern the plan

DyDiT (arXiv 2410.03456, code public at alibaba-damo-academy/DyDiT) reports
**51% FLOPs reduction → 1.73× wall-clock speedup.**

That is a **~3× gap between the compute you saved and the time you saved.** Skipping the
MLP while still paying for full attention does not convert FLOPs into time. AdaDiff reports
~45% acceleration; DDiT claims 3.52× on FLUX-1.Dev, which the scout explicitly declines to
believe without profiling.

**Any design that reports FLOPs savings and does not report wall-clock has not measured the
thing that costs money.**

## Why #4 is the only one to build

DyDiT's spatial router is **trained end-to-end against the noise-prediction loss**. The
proposal here reads **calibrated confidences from an external model** instead. That delta is
real, untested, and cheap to kill — which is exactly the profile of an experiment worth
running.

And exp4 is the first evidence about it, and it is not good news: the discrete judge was
**statistically indistinguishable from a free local-noise heuristic** and 56% below the oracle
ceiling. If the scout is right that this is the open question, then exp4 is a **negative
first result** on the open question, and the next experiment has to explain it rather than
repeat it.

**DuoDiff supplies the counter-result that should shape the design**: early exit fires
consistently at *high-noise* steps and rarely at low-noise ones, and a uniform static
schedule loses to an adaptive one. A judge that flags coordinates uniformly will lose.

## Why #2 should not be built as specified

Two independent documented failures:

- Test-time correction: *"in these distilled models, even infinitesimal test-time gradients
  often trigger reward collapse and fail to mitigate cumulative error."* They abandon
  parameter-space optimisation **for** sampling-space intervention.
- DDPO: updating on the conditional objective alone *"rapidly deteriorated after the first
  round of finetuning… the guidance weight becomes miscalibrated each time the model is
  updated."*

Plus a structural problem nobody has solved: the reverse SDE is defined against a **fixed**
score function. Mutating the generator mid-trajectory means you are no longer sampling the
distribution you think you are, and there is no theory for it.

**Diffusion-TTA survives because it mutates the *discriminative* model and keeps the
diffusion model frozen.** That is the safe direction, and it is the one with code.

## The methodological note, which is the part I would keep

The scout guessed three arXiv IDs wrong and caught all three — a facial-reaction paper, a
NER paper, an RFID-localisation paper. It also refused to rely on several IDs in a
plausible-but-unconfirmable range that surfaced with confident-looking abstracts, and
excluded them from its reasoning.

**That is the discipline this whole project has been relearning all session, arriving at from
the other end.** A confident citation is not a verified citation. The three mis-guesses are
worth more than the thirty correct ones, because they are the receipt.

## What this changes in the roadmap

- **#4 is now lane one**, and the experiment is sharper: an external calibrated router vs a
  trained one, on a task with a *known* phase structure, measured in wall-clock.
- **#1 is a perf PR, not a paper.** The mechanism is solved. The VRAM claim is overstated:
  you save activations, not the second model's weights. Read Latent-CLIP first — it may make
  the kernel moot.
- **#3 splits.** Seams are solved (MultiDiffusion, MosaicFusion). Global coherence is *open*
  (CoFi, CDGS attack it with expensive multi-pass search). Expect a working blender and a
  disappointing router.
- **#2 is dropped** in its specified form. If closed-loop benefit is wanted, build
  Diffusion-TTA's version: freeze the generator, mutate the judge.

## The one bit that is genuinely unclaimed

Using **boundary logits as the inter-canvas wire format**. Nobody does that. It is a small
delta on MIGC and RAG, and it is the only part of #3 worth a novelty claim.
