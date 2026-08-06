# Foundry Round 3 — H5: an operational severity observable

## Why this target

Rounds 1 and 2 both proposed **mechanisms** ("here is how the world
works"). Mechanism-space is exhaustively mapped, so both landed on named
prior art — Round 1 on algebra, Round 2 on pattern formation. Round 3
changes axis again: propose a missing **observable**. New instruments
historically open more ground than new formalisms.

Which observable? The one this session produced hard evidence for. The
single most reliable empirical regularity across all of this work is not
about flow networks at all:

> **I built four tests whose outcome was fixed by their construction
> rather than by the system under study, and I could not detect a single
> one from the inside.** All four were caught by adversarial review —
> H1's fan-out test (hard-coded `True`), H2's impossibility search
> (scoped to always confirm), T4's P1 (taper provably inert across the
> entire kill window), H4's C2 (diffusion length 0.45 cells — the
> zero-diffusion limit).

I even wrote an explicit anti-vacuity statement at the top of T4 and
then committed the error anyway, in the same file. Writing the warning
did not help. That is a measurement problem, and there is no instrument
for it.

## H5 — the vacuity/severity observable

**Claim.** A test's severity is computable *before trusting its result*,
by asking whether its verdict depends on the mechanism the hypothesis
holds responsible:

    S = relative change in the test's measured quantity
        when the claimed-responsible mechanism is toggled or swept

- **S ≈ 0** — toggling the mechanism changes nothing. The mechanism is
  inert in the tested regime; the verdict was fixed by construction.
  **Vacuous.**
- **S large** — the verdict tracks the mechanism. The test is actually
  measuring the thing it claims to measure. **Severe.**

Stated plainly it sounds trivial — *does your independent variable
actually vary?* Its interest is entirely empirical: I failed it four
times in a row while believing I was being careful, so if it works it
catches errors that care and pre-registration demonstrably do not.

## Why this is testable on real ground truth (not another toy)

This session has already produced **labelled** examples, adjudicated by
hostile reviewers with no stake in the outcome:

| test | known label | source of label |
|---|---|---|
| H1 `test_c3_no_fanout` | VACUOUS | adversary: hard-coded `True` |
| T4 P1 threshold | VACUOUS | adversary: taper inert to 1e-17 |
| H4 C2 individuation | VACUOUS | adversary: D-length 0.45 cells |
| H2 `test_and` | SEVERE | genuine 4-row truth table |
| T6d L7 fresh points | SEVERE | survived hostile review |
| T6e boundary | SEVERE | predicted adversary's counterexample |

The instrument is scored against these labels **without being given
them**.

## Pre-registration (before writing `h5_sim.py`)

**P1:** S < 0.05 for all three known-vacuous tests.
**P2:** S > 0.5 for all three known-severe tests.
**P3:** clean separation — no overlap between the two groups.
**Kill:** any overlap, or any single misclassification. An instrument
that cannot reproduce labels already established by adversarial review
on the very cases that motivated it is dead, regardless of novelty.

## Meta-pre-registration

Round 1 died to algebra; Round 2 died to pattern formation (predicted
in advance, confirmed). I predict Round 3 dies to a **fourth family:
methodology** — specifically **mutation testing** from software
engineering (mutate the system, check whether the test notices),
**statistical power / severity** (Mayo), **sensitivity analysis**, or
**Youden's J** (sensitivity + specificity − 1), which is close to what S
computes if framed as a discrimination statistic.

If it dies there, the strategy-relocation result holds for a third
consecutive round and "generate differently" is confirmed as a
controllable variable across three distinct regions.

**The difference from H1–H4:** a reduction kill would not make this
useless. (Placeholder retained; results below.) If S is mutation testing rediscovered, it *still catches the
four errors I could not catch myself*, and it is still an instrument
this repository demonstrably needs. Novelty and utility come apart here
for the first time in the foundry — which is itself worth recording.

---

# H5 RESULTS — **FAILED its pre-registration**

```
                  test        S  instrument says  true label
  H1 test_c3_no_fanout   0.0000          VACUOUS     VACUOUS  ok
           H2 test_and   1.0000           SEVERE      SEVERE  ok
       T4 P1 threshold   0.0000          VACUOUS     VACUOUS  ok
   H4 C2 individuation   0.0065          VACUOUS     VACUOUS  ok
   T6d L7 fresh points   0.8182           SEVERE      SEVERE  ok
          T6e boundary   0.3123        AMBIGUOUS     SEVERE   MISCLASSIFIED

P1 all vacuous S < 0.05:  0.0065 -> PASS
P2 all severe  S > 0.50:  0.3123 -> FAIL
P3 clean separation:      gap +0.3058 -> PASS
```

**Verdict: FAILED.** The kill condition was "any overlap, or any single
misclassification." T6e scored 0.3123 — below the pre-registered 0.5
severity bar — so P2 failed and one of six was misclassified. H5 is
recorded as failing, per the rule written in advance.

**What is nonetheless true, and what is not.** The three known-vacuous
tests scored 0.0000, 0.0000, 0.0065; the three known-severe scored
0.3123, 0.8182, 1.0000. **Separation is perfect — a gap of 0.306 with
nothing in between.** The instrument's *ordering* reproduced the
adversarial labels exactly; only my *absolute threshold* was wrong.

I want to name the pattern rather than excuse it: **this is the third
time this session I have pre-registered a numeric threshold tighter or
more arbitrary than the measurement could support** (T4's P1 window,
T6b's 5% floor-law bar, now H5's 0.5 severity bar). The kill conditions
keep being right to fire; my constants keep being guesses dressed as
predictions. Moving the bar to 0.3 now would be pure post-hoc fitting,
so I am not doing it. A real fix requires deriving the threshold from
principle, or abandoning absolute thresholds for the separation
statistic — and either must be tested on cases not used to construct it.

## Scope test — and my prediction about it was also wrong

Pre-registered before running: H3's C1 was killed by its adversary as
**rigged** (strawman never-decaying LFU baseline), a *different* failure
class from inert-mechanism vacuity. Since H3's decay mechanism genuinely
varies, I predicted S would score it **high (>0.5, "SEVERE")**, giving a
clean false negative that bounds S's scope.

**Measured S = 0.0574 → "AMBIGUOUS".** The prediction was wrong: S
scored it near the vacuous band, not the severe one. The scope
limitation is real — S is not detecting what was actually wrong with H3
(a weak baseline, which S has no access to) — but it fails in a
direction I did not anticipate, so even my account of my own
instrument's failure mode was wrong on first attempt.

**Net: S detects inert-mechanism vacuity (3/3, decisively, at ~0) and
ranks severity correctly (3/3), but its absolute scale is uncalibrated,
it misses baseline-rigging entirely, and it failed the bar I set for
it.**

---

# H5 ADVERSARY VERDICT — **KILLED(rigged)**

Independently verified before acceptance. The decisive finding:

```
SHIPPED windows:
  T6d (true SEVERE)  [0.10,0.25,0.50,1.00]  S=0.8182
  H4  (true VACUOUS) [0.0, 1e-4]            S=0.0065

ALTERNATIVE, equally defensible windows:
  T6d (true SEVERE)  [0.9, 1.0, 1.1]        S=0.0990
  H4  (true VACUOUS) [0.0, 0.01]            S=0.1454

ORDERING INVERTED: vacuous 0.1454 > severe 0.0990
```

**My rescue argument is dead.** I claimed that although the absolute
threshold failed, "the instrument's *ordering* reproduced the
adversarial labels exactly." It does not. The ordering inverts under
different but equally defensible sweep windows — a known-vacuous test
outscores a known-severe one. The clean 0.306 separation was never a
property of S; it was **a property of the eight numbers I happened to
type into six function bodies.**

The line that lands hardest, and is correct:

> "The paper never swept the sweep, i.e. it never asked S of itself."

**H5 fails its own test.** An instrument for detecting verdicts fixed by
construction had its own headline verdict fixed by construction — one
run, one hand-picked set of sweep points per case, no sensitivity check
of the sensitivity index. This is the same error a fifth time, now
committed *inside the tool built to catch it*.

Two further defects, both correct:
1. **`case_h1_fanout`'s S=0 is analytically guaranteed, not measured.**
   `test_c3_no_fanout` never calls `Substrate.clone`; its return value
   is a tautology. The swept variable never touches the measured code
   path, so that row could not have come out otherwise — it is a
   vacuous test *of* vacuity, inside the vacuity detector.
2. **The harness's AMBIGUOUS band spans 45% of the unit interval**
   against binary ground truth, so a misclassification was close to
   guaranteed by scoring design rather than by measurement.

**Reduction** (as pre-registered): OAT range / elementary-effect
sensitivity index, Morris-screening family — a class where exactly this
window-dependence is textbook-documented. Not Sobol (no variance
decomposition), not properly Mayo severity (no probability model over a
reference class).

**One thing survives.** `case_t4_p1` is robust: S stays at ~1e-16 to
2e-5 for every I_cap from 0.05 to 1.0. The taper really is inert there
regardless of window. That is a genuine finding about T4, independent of
range choice — and the *only* row in the table that is.

## Meta-experiment: third consecutive relocation confirmed

Round 1 → algebra. Round 2 → pattern formation (predicted). Round 3 →
methodology / OAT sensitivity analysis (predicted). Three rounds, three
distinct prior-art families, each named in advance. **"Generate
differently" is confirmed as a controllable variable** — it reliably
moves the search into a new region. It has not once produced a region
that was unoccupied.

**Foundry standing: 0 for 5.**

## The finding this round actually produced

Not an instrument. A correction to my own diagnosis. I had written that
my recurring error was "pre-registering thresholds tighter than the
measurement supports." The adversary showed that undersells it:

> **The measurement itself is not stable enough to support *any*
> threshold, tight or loose, without first specifying and defending a
> canonical perturbation range — which the pre-registration never did.**

The failure was never in the constants. It was in believing a number was
a measurement before checking whether it was stable under choices I had
made without noticing I was making them.
