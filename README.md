# jev-fusion — testing four claims about fusing a discrete judge into a generative loop

Four architectures have been proposed for making a fast discrete decision model (a "Jev"-style
System One returning typed probabilities) *govern* a continuous generative process rather than
merely judge its output. They are written as architecture prose. This repository turns each
into a falsifiable experiment, and records which survive.

| # | claim | experiment | status |
|---|---|---|---|
| 1 | a discrete decision can act as a geometric constraint *before* the output exists | `exp1_projection.py` | see findings |
| 2 | updating parameters *during* sampling beats correcting afterwards | `exp2_closed_loop.py` | see findings |
| 3 | local per-canvas generation + a central router keeps global coherence | `exp3_multicanvas.py` | see findings |
| 4 | spending compute only where a fast judge flags beats a full pass | `exp4_selective.py` | see findings |

**The method is the method, not the pixels.** A real diffusion backbone costs GPU-hours and
would make these results un-reproducible. Each experiment uses the same structure with a
tractable surrogate generator whose ground truth is known exactly, so the *control* is
available. The claim under test is always about the CONTROL STRUCTURE — when to spend, what to
condition on, whether the loop closes — never about image quality.

**The instrument is the same discrete judge in every experiment**, called through the
documented contract (`state` is a string; the option set IS the `criteria` keys). Its own
discrimination is verified by a control in `jev_check.py` before any experiment is believed.
