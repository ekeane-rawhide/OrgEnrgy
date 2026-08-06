# Ledger — Adaptive-γ / Self-Tuning Criticality

Continuation of the deposition/decay/routing universality investigation.
Format: pre-registration (prediction + kill condition) written before each
run, then the result and verdict. See `HANDOFF.md` for the prior session's
laws (L1–L5) and failures (F1–F3), which this work builds on without
re-litigating.

New formula under test:

    dC_i/dt = α F · C_i^γ(t) / Σ_j C_j^γ(t) − β C_i
    dγ/dt   = κ ( γ_target(σ_F) − γ )
    γ_target(σ_F) = γ_max − (γ_max − γ_min) · g(σ_F)

---

## Step 0 — analytic check: does adding γ-dynamics move the critical point?

**Pre-registration (before deriving):**
Prediction: for κ ≪ β, the critical point stays exactly at γ=1 pointwise in
time, because the coupled Jacobian is block-triangular — the γ-row has no
dependence on x_i (γ_target depends only on the exogenous stress signal
σ_F, not on the channel state), so it contributes no cross term into the
x-block eigenvalue. Kill condition: if γ_target is ever defined as a
function of the C_i themselves (not just of F/σ_F), this block-triangular
argument breaks and the critical point must be rederived numerically.

**Derivation.**
S = Σ_i C_i still obeys dS/dt = αF − βS regardless of γ, since the
routing fractions C_i^γ/Σ_j C_j^γ sum to 1 for any γ. So **S\* = αF/β is
unaffected by making γ dynamic** — this generalizes cleanly, not just
survives.

At x_i = C_i/S, replicator form dx_i/dt = β(x_i^γ(t)/Σ_j x_j^γ(t) − x_i)
is unchanged in shape; γ(t) enters parametrically. The full state is
(x_1..x_N, γ). Linearizing about (uniform x, γ0):

- x-block: same as L1, eigenvalue β(γ0 − 1) (evaluated at instantaneous γ)
- γ-block: d(δγ)/dt = −κ δγ + κ (∂γ_target/∂σ_F)(∂σ_F/∂x_i) δx_i

The second term in the γ-row is the only possible cross term, and it is
exactly zero under the stated design (σ_F is a statistic of the exogenous
flow F, not of the channel occupancies x_i). So the Jacobian is
block-triangular: eigenvalues are exactly {β(γ0−1) [×(N−1)], 0 [S-mode],
−κ [γ-mode]}, with no coupling correction term at any order in this
linearization — the two blocks simply don't talk to each other.

**Verdict: PASSED.** Critical point stays at γ=1 for any κ, not just
κ≪β, *provided* σ_F is exogenous to the channel state. This is a stronger
and cheaper result than what was pre-registered (didn't even need the
timescale-separation assumption at the linear level) — flagging that the
adiabatic-tracking question in Step 2 is about the *nonlinear* transient
(how N_eff(t) lags γ_target(t) away from equilibrium), not about whether
the fixed point moves, which it provably does not.

---

## Step 1 — regression: reproduce L1 with κ=0

**Pre-registration:** with γ-dynamics disabled (κ=0, γ held fixed), the
new harness (`sim5.py`) must reproduce the L1 eigenvalue curve
β(γ−1) to the same ≈3e-4 tolerance as the prior session's `sim1.py`,
γ ∈ [0.4, 1.8], N=20. This is a harness sanity check, not a new claim —
failure here means a bug in the new code, not a physics result.

**Result:** `sim5.py`, γ∈[0.4,1.8] (15 points), N=20, β=1.0, κ=0.
Eigenvalue measured by perturbing the uniform fixed point and fitting the
exponential growth/decay rate of ‖x−x_uniform‖ in the linear regime
(‖ε‖ < 10·ε0). Max abs error 3.69e-4, worst at the γ=1.8 edge; error grows
monotonically with |γ−1| in both directions, consistent with dt-truncation
scaling with |eigenvalue| rather than a harness bug (matches the pattern of
the original `sim1.py`, which reported the same order of tolerance). γ=1.0
recovers the L2 zero eigenvalue exactly (3e-16, float noise).

**Verdict: PASSED** (within ~1.2× of the 3e-4 target, same failure shape as
the reference implementation — treated as harness-clean, not re-tuned to
force a tighter number).

---

## Step 2 — adiabatic tracking: does N_eff(t) track γ_target(σ_F(t)) with lag ≈ 1/κ?

**Pre-registration (before running):**
Drive γ_target with a step change (γ_target: 0.7 → 1.3, i.e. distributed →
monopoly bias) at fixed κ, and integrate the full coupled system
(x_i(t), γ(t)) — no separate σ_F process yet, γ_target stepped directly,
since Step 0 established the block-triangular argument only needs γ_target
to be exogenous to x, not any particular σ_F functional form.

Prediction: N_eff(t) = 1/Σx_i(t)² relaxes from its γ=0.7 equilibrium value
toward its γ=1.3 equilibrium value with an observable lag set by κ, and for
κ ≪ β the observed 10%–90% rise time of N_eff should be within 2× of the
naive γ-only estimate 2.2/κ (a standard first-order-lag rise-time
approximation, since γ(t) itself is a simple exponential relaxation to the
new target with rate κ). Kill condition: rise time > 2× that estimate, or
non-monotonic overshoot in N_eff, for any κ ∈ {β/50, β/10, β/3}. Overshoot
or a rise time blown out past 2× would mean the x-dynamics do not simply
"ride along" behind the slowly moving γ, and the adiabatic/self-tuning
framing needs a nonlinear correction term, not just a first-order lag model.

**Result:** `t5_adiabatic.py`, β=1, N=20, step γ_target: 0.7→1.3, κ ∈
{β/50, β/10, β/3}.

Literal kill condition (rise time > 2× predicted, or overshoot): **not
triggered**. No overshoot at any κ. Measured 10–90% rise times (7.5, 6.6,
6.6) were *shorter* than the naive prediction 2.2/κ (110, 22, 6.6) —
opposite direction from what the kill condition was written to catch.

But treating that as a pass would be following the letter, not the
substance, of the pre-registration. Digging into *when* the transition
happens (not just its width) found the real effect: for κ=0.02, N_eff
doesn't even begin dropping until γ(t) has already reached 1.258 — 86% of
the way to its 1.3 target — and the same clustering (γ at the 50%-transition
point = 1.300 / 1.300 / 1.299 / 1.291 / 1.262 / 1.235 for
κ = 0.333/0.2/0.1/0.05/0.02/0.01) shows almost no dependence on κ over a
33× range. **x does not track γ_target with a lag proportional to 1/κ. It
stays pinned near its old-phase value while γ sweeps through the critical
region, and only transitions once γ has swept nearly all the way to its
new target — regardless of how slowly γ moved.**

This is not a numerical artifact — it's a direct, derivable consequence of
L1 + L2 that the pre-registration failed to account for: the x-relaxation
rate is λ(γ) = β(γ−1), which **vanishes at γ=1**. Adiabatic tracking
requires κ ≪ λ(γ(t)) at every instant, but λ→0 exactly where γ(t) crosses
1, so there is an unavoidable non-adiabatic window around the phase
boundary in which x cannot possibly keep up, no matter how small κ is made
— shrinking κ slows γ down, but it doesn't fix the fact that λ still hits
zero at the crossing. This is critical slowing down (L3) acting on the
*dynamic* passage through the boundary, not just on convergence at a fixed
γ near it.

**Verdict: literal pre-registration PASSED, substantive hypothesis
FALSIFIED.** Recorded as a falsification rather than claimed as a pass,
per the method discipline (don't let a loosely-worded kill condition
launder a wrong model into a "success"). Renaming the effect **pinning
delay**. Consequence for Step 3: the entire resilience argument for
self-tuning criticality assumed the structure redistributes promptly once
stress is detected and γ_target drops. Pinning delay means that is false
near the boundary — the system can remain concentrated for a long stretch
after a stress signal has fired, which is precisely the failure mode a
resilience mechanism is supposed to prevent. Step 3 must measure this
directly (time from failure injection to actual redistribution, not just
whether redistribution eventually happens) rather than assume the Step 2
model.

---

## Step 3 — resilience payoff test, revised after the pinning-delay finding

**Design note before pre-registering:** a channel with C_i=0 under pure
preferential routing (x_i^γ/Σx_j^γ) can never regrow, since 0^γ=0 for γ>0
— this is L2's absorbing state, now recognized as a hard blocker for any
resilience claim: in the monopoly phase, non-dominant channels sit at
effectively zero, so after a failure of the dominant channel there is
nothing for flow to redistribute *to* without an explicit floor. The L4
admixture (p_i = (1−m)x_i^γ/Σx_j^γ + m/N) is therefore used here not as an
optional add-on but as a structural prerequisite for recoverability, with
m=0.05 fixed a priori (not tuned to the outcome) and the threshold
correction γ*=1/(1−m)=1.053 carried through.

**Pre-registration (before running):**
N=20, β=1, m=0.05. Baseline γ_target=1.4 (monopoly-favoring, above
γ*=1.053) held until the system reaches its monopoly steady state. Then:
(a) fail the dominant channel (set its x_i to 1e-6, renormalize the rest),
and (b) simultaneously step γ_target down to 0.6 (below γ*) for a fixed
20 β⁻¹-unit stress window, then return it to 1.4. Compare against a fixed
γ=1.4 control that experiences the same channel failure but no γ_target
response.

Metrics: minimum post-failure N_eff (vulnerability depth — lower means
more exposed to a second failure hitting an already-thin set of channels)
and time for N_eff to recover to N/2.

Given the Step 2 finding, the naive resilience story (fast redistribution
the moment stress is detected) is now suspect. Explicit prediction:
adaptive-γ's minimum post-failure N_eff will be **higher** than the fixed
control's (some benefit survives, because the pre-failure state under
adaptive is not different from fixed — the two only diverge after the
event, and any redistribution beats none) but the **improvement will be
smaller than a naive lag-free model would predict**, and recovery will not
begin promptly — consistent with pinning delay. Kill condition: if
adaptive-γ's minimum post-failure N_eff is not at least 10% better than
the fixed control, the resilience claim is falsified outright, independent
of Steps 0–2.

**Result:** `t5_resilience.py`, N=20, β=1, m=0.05, κ=0.1, γ_base=1.4,
γ_stress=0.6, stress window 20 β⁻¹ units, failure = kill the dominant
channel (whichever holds the largest share at steady state) and
renormalize.

**Two bugs caught before the result could be trusted, both left visible in
the code/history rather than silently patched:**

1. First run: killing the dominant channel and renormalizing among
   survivors left them in an *exactly* symmetric tie (no noise), which is
   an unstable-but-unbroken fixed point of the deterministic ODE — nothing
   ever re-concentrated, in either the adaptive or fixed run, so the test
   was measuring nothing. Fixed by adding a small perturbation
   (1e-3 relative noise) to survivors post-failure, matching the noise
   scale already used to seed initial conditions elsewhere in this
   codebase — not a new free parameter chosen to produce an effect.
2. The pre-registered metric itself ("minimum N_eff over the whole
   post-failure trajectory") was wrong: with noise restored, *both*
   adaptive and fixed runs eventually re-concentrate to the same monopoly
   fixed point once γ returns to baseline (that's the correct, expected
   behavior — γ_base=1.4 is monopoly-favoring in both cases). So "eventual
   minimum" only measures how far each trajectory got by T_post, not any
   real difference between the two policies. Replaced with the metric the
   pre-registration was actually trying to get at: **how long does the
   post-failure redistributed state hold before re-concentrating past a
   danger threshold (N_eff<5)** — i.e., how much safe window does the
   policy buy before a second failure could hit an already-thin structure
   again.

**Corrected result**, 6 seeds: adaptive-γ holds N_eff above the danger
threshold for a mean of 67.4 β⁻¹ time units vs 21.6 for the fixed-γ=1.4
control — a **3.13× ratio**, consistent across seeds (3.04–3.20×, no
overlap). Supporting metrics: time-integrated N_eff over the first 60
units (a stand-in for cumulative resilience "credit") is +167.9% higher
for adaptive; at t=20 (end of the stress window) adaptive sits at
N_eff=20.0 (fully redistributed, matching N) vs 13.0 for fixed (already
re-concentrating).

Note this **does not contradict** the Step 2 pinning-delay finding — it
confirms and contextualizes it. Pinning delay says γ crossing the boundary
doesn't instantly redistribute structure; it's still true here (N_eff
doesn't reach its ceiling of 20 immediately — see the t=20 checkpoint,
which is already after most of the stress window has elapsed). What Step 3
adds: even a *delayed, partial* redistribution response beats no response
at all by a wide margin, because the fixed-γ control has no opposing force
at all against re-concentration. The resilience benefit is real but should
not be oversold as fast.

**Verdict: PASSED**, with a large margin (3.13× vs the 1.10× kill bar) —
but the margin is measured on a metric that had to be rebuilt mid-test
after catching that the pre-registered one was vacuous. Treat the *sign*
and *rough magnitude* of this result as solid; treat "3.13×" as this
specific scenario's number, not a universal constant — γ_stress, m, κ, and
the danger threshold were all fixed a priori but not swept, so this is one
point, not a curve.

---

## L6 — generalized critical-point law for an arbitrary routing kernel (new, this session)

Before attempting Step 4's domain mapping, checked a cheaper and more
general question first (cheapest-kill-first applies to *analysis* steps
too, not just simulations): does L3's N-invariant critical point survive
if a real domain's native allocation rule isn't literally a power law?

**Pre-registration:** linearizing dx_i/dt = β(f(x_i)/Σf(x_j) − x_i) about
uniform x*=1/N for a general smooth kernel f predicts eigenvalue
λ = β(γ_eff(N) − 1), γ_eff(N) ≡ x\*f'(x\*)/f(x\*) — the *local elasticity*
of f at the uniform point. For f(x)=x^γ, elasticity is constant (=γ,
independent of x), which is exactly why L1/L3 found the threshold at
γ=1 independent of N. For a non-power-law kernel, elasticity generically
depends on x*=1/N, so the critical parameter should shift with N. Tested
against f(x)=exp(x/T) (softmax/diode-OR-style competition), predicted
γ_eff = (1/N)/T, hence critical T\*=1/N.

**Result:** `sim6_general_kernel.py`. Power-law regression at γ=1
reproduces exactly 0 for N=10/20/40 (sanity check). Exponential kernel:
predicted vs measured eigenvalue matches to ≤1.6e-4 across N∈{10,20,40}
and T∈{0.7,1.0,1.3}×T\*, and the critical T\* scales as exactly 1/N as
predicted (confirmed at all three N).

**Verdict: PASSED.** New generalization, call it **L6**: *N-invariance of
the critical point (L3) is not a generic property of preferential routing
— it is a special consequence of the power-law kernel's scale invariance
(constant elasticity). A domain whose native allocation mechanism is not a
true power law (e.g. exponential/softmax competition, common in physical
winner-take-most circuits like diode-OR arbitration between energy
sources) will have a critical point that depends on system size,* the
opposite of what makes the abstract model's "one dimensionless parameter,
domain-independent" claim interesting.

**Consequence for Step 4:** before building any domain simulation, check
whether the domain's actual sharing mechanism is a true power law (in
which case L1–L5 transfer with N-invariance intact) or something else
(exponential, sigmoid, threshold/winner-take-all) — in which case a
domain-specific, N-dependent critical curve applies instead, derivable
from the same elasticity formula but not equal to the abstract model's
clean γ=1. See `DOMAIN_MAPPING.md`.

---

# WILD HYPOTHESIS FOUNDRY (new branch of work)

Maximal-novelty loop: hypotheses generated from instinct with no
literature input, then adversarially attacked by independent subagents
whose brief is to kill them (equivalence reduction to known work counts
as a kill). Specs in `wild/`. Order: H2 (calibration corpse) → H1 → H3.
H2 is *designed* to be killable — if the adversaries fail to kill it,
the kill process is too weak and nothing else's survival means anything.

## H2 pre-registration (before running h2_sim.py)

Predictions: C1 (AND) and C2 (OR) implementable — PASS. C3: NOT is
impossible because all three primitives are monotone in arrival times;
exhaustive depth-3 search finds no NOT — PASS, establishing
sub-universality without an inhibitory primitive.
Adversary prediction (recorded here, NOT shown to adversaries): they
should kill H2 as a rediscovery of race logic / temporal or spiking
computation. Calibration gate: if no adversary lands that kill, HALT the
foundry and report process failure.

## H1 pre-registration (before running h1_sim.py)

Predictions: single-use enforcement PASSES (double-spend of a consumed
delta raises), provenance composition PASSES (δ(a,b)∘δ(b,c)=δ(a,c)),
fan-out is IMPOSSIBLE by construction (no copy operation exists), and
therefore any Boolean circuit needing an input twice is unimplementable →
sub-universal.
Adversary prediction (not shown to them): kill as groupoid composition +
linear-logic/linear-types resource discipline.

## H3 pre-registration (before running h3_sim.py)

Task: next-item top-N prediction on a drifting Zipf stream (K=200 items,
budget N=32, distribution re-permuted every 2000 steps). Predictions:
rented-memory (decay-scored) machine beats exact-count LFU under drift
(hit-rate gap ≥ 5 points after first drift event); approximately ties an
EMA-scored baseline — because (recorded honestly, in advance) the closed
form of the rented store IS an EMA of access flow, C(t) = αΣ(1−β)^(t−s),
so the likely verdict is KILLED(reduction to decayed-frequency caching).
Adversary prediction (not shown to them): they land exactly that
reduction.

## Foundry sim results (all three, before adversary verdicts arrived)

**H2** (`wild/h2_sim.py`): C1 AND — PASS (4/4 truth-table rows).
C2 OR — PASS (4/4). C3 — PASS: exhaustive search over all reachable
signal pairs at depth ≤3 (73 pairs) finds no NOT circuit, consistent
with the monotonicity argument. All three predictions confirmed.

**H1** (`wild/h1_sim.py`): C1 single-use — PASS (double-read and
double-fuse both raise substrate faults). C2 provenance — PASS
(δ(a,b)⊕δ(b,c)⊕δ(c,d) → δ(a,d), genesis set names all 3 mint events).
C3 no-fan-out — PASS (no operation yields two live deltas from one).
All three predictions confirmed. Note recorded before the adversary
reports: C1 and C3 are dangerously close to restating the axioms —
whether they count as *tests* at all is exactly the kind of thing the
adversary round exists to judge.

**H3** (`wild/h3_sim.py`): 5 seeds, K=200, N=32, drift every 2000 steps.
C1 — PASS: hit-rate after first drift 67.9% (rented) vs 60.2% (LFU),
gap +7.7 points (pre-registered bar: ≥5); by the steady-drift window the
gap widens to 67.6% vs 48.9% as LFU's stale counts compound. C2 — the
honest self-kill CONFIRMED: max deviation between the substrate's scores
and the closed-form EMA of access flow is 7.1e-15 (machine precision).
The substrate is literally an exponentially-decayed frequency counter.
Both predictions confirmed, including the one that guts the hypothesis.

## H2 adversary verdict (calibration gate)

**VERDICT: KILLED(reduction).** The adversary landed the predicted kill
and then some. Named prior art, quoted from its report: diode logic
("the canonical real-world instance of AND+OR without NOT"), **Race
Logic** (Madhavan & Sherwood et al., ISCA 2016 — "already names,
formalizes, and ships the exact substrate H2 claims to discover"),
(min,+)/(max,+) tropical semiring / network calculus (Baccelli et al.),
activation-only gene-regulatory networks, and the monotone-circuit
theorem itself (Wegener; Razborov's monotone lower bounds).

The adversary also found two things I did NOT plant:
1. **A real internal flaw**: my spec asserts the coincidence gate is "a
   monotone function of arrival times" in general. False — outside the
   coincidence window the output is silence, so as a function on ℝ the
   gate is a non-monotone bump; it is monotone only on the two-point
   encoding domain the sim restricts to. The spec claimed a general
   theorem and quietly discharged only a domain-restricted version.
   Legitimate KILLED(inconsistent) grounds independent of the reduction.
2. The "exhaustive" NOT-search is scoped (depth ≤3, two seed times) just
   narrowly enough to always vindicate the hypothesis — a de-facto
   confirmation-only test.

**CALIBRATION GATE: PASSED.** The kill process demonstrably works at
full strength — it found the planted kill *and* two unplanted flaws.
H1/H3 adversary verdicts can now be taken seriously.

## H3 adversary verdict

**VERDICT: KILLED(reduction)** — the pre-registered prediction landed
exactly, and the adversary went further than my own self-test did.

Named prior art from its report: **LRFU** (Lee et al., 1999/2001 — the
CRF score Σ F(t−t_k) with F(x)=(1/2)^(λx) is "the identical
exponential-decay accumulate-on-access score, differing only by
re-basing," 1−β = 2^(−λ)); **TD(λ) eligibility traces** (Sutton & Barto
— same first-order linear recursion, decades older); **EWMA / Jacobson's
RTT estimator**; and the deployed aging family (Redis approximate-LFU
decay counters, Squid cache aging, Window-TinyLFU periodic halving).
Its summary of my C2 self-test: "I'm just cashing that check" — C2 was
algebra, not an empirical test; it could never have failed.

Additional unplanted kill: **C1's baseline was rigged**. Pure
never-decaying LFU is a known-pathological strawman under drift — every
real deployed LFU variant (Redis, Caffeine, LFU-Aging) includes decay or
windowing precisely because this failure mode has been documented for
decades. A fair baseline (LRFU itself, sliding-window counts) would
likely erase most of the +7.7-point gap, since it would then be two
decay schemes differing in detail. The numbers were real; the comparison
was against an opponent nobody would deploy.

Verdict accepted without repair attempt: both kills are independently
fatal and the reduction was pre-registered as the likely outcome.

## H1 adversary verdict

**VERDICT: KILLED(reduction)** — the predicted kill (groupoid + linear
logic) landed, plus three more named reductions and a rigged test I
wrote without noticing.

Axiom-by-axiom decode from its report: differences = morphisms in a
category (Yoneda-style relationalism); fusion = categorical composition
with **linear logic** (Girard 1987) consumption semantics — also **Petri
net** token flow (1962); destructive read = linear elimination /
projective quantum measurement; axiom 4 is "word-for-word the
**no-cloning theorem** (Wootters & Zurek 1982; Dieks 1982)"; free
inversion = the **groupoid** axiom (Brandt 1927), and the full package
(invertible + uncopyable + destructive read) is the standard structure
of **categorical quantum mechanics** (Abramsky & Coecke dagger-compact
categories). C3's headline claim — no fan-out ⇒ sub-universal — "is
precisely why Girard introduced the ! modality": the
multiplicative-only fragment of linear logic has been known to be
sub-universal on exactly this point for ~40 years. The predicted
capability (uncloneable tokens without cryptography) is the standard
pitch for **Wiesner's quantum money** (~1970/1983) and for linear-type
systems (Rust ownership, uniqueness typing).

Unplanted find: my `test_c3_no_fanout` was **vacuous** — it repeats the
C1 double-read test under a new name and asserts a hard-coded True
(`single_output` comes from a comprehension that cannot produce False
for any implementation, correct or broken). It cannot fail, tests
nothing about fan-out, and I did not notice when writing it. The
adversary is right that a real C3 test would need to show no combination
of mint/fuse/invert/read builds AND(x,x) — an argument I made in prose
only.

Verdict accepted without repair attempt.

## Foundry final tally

H1: KILLED(reduction) — linear logic + groupoids + no-cloning + quantum
money. H2: KILLED(reduction) — race logic + diode logic + tropical
semirings (calibration corpse, executed as designed). H3:
KILLED(reduction) — LRFU + eligibility traces + EWMA aging.
Three for three, all landing on the pre-registered predictions, plus
four unplanted flaws found (one false theorem statement, one scoped
search, one rigged baseline, one vacuous test). Full accounting and
what this measures in `wild/VERDICT.md`.

---

# T4 — MICROGRID DOMAIN TEST (the never-run experiment)

The original handoff's item A, never executed in three sessions.
`DOMAIN_MAPPING.md` selected this domain because it passes both
structural checks (shared competition pool; power-law kernel by
construction). This is the first test of the model against something
with physics in it rather than against itself.

## Anti-vacuity statement (written first, deliberately)

The adversaries killed two of my tests for being restatements of their
own premises. So, before designing this one: **if this simulation merely
re-implemented dC_i/dt = αF·C_i^γ/ΣC_j^γ − βC_i with variables renamed
to "cells" and "bus", the test would be worthless** — it would
rediscover L1 by construction, exactly the failure mode already caught
twice. The test is only meaningful if the simulated system contains
dynamics the abstract model does **not** have, and we ask whether the
γ=1 threshold survives them.

Physics added here that has no analogue in the abstract ODE:
1. **State of charge** SOC_i as a second state variable per cell (the
   abstract model has one variable per channel, not two).
2. **Constant-voltage taper**: a cell's acceptance limit falls as
   I_cap·(1−SOC_i) — real charging behavior. A full cell physically
   refuses current no matter what the controller allocates.
3. **Rejected-current redistribution**: what a saturated cell refuses is
   re-offered to the others, weight-proportionally, over several rounds.
4. **Load draw** proportional to stored charge, giving cells a discharge
   path and a genuine equilibrium.

Crucially, (2) creates a **feedback from physical state onto the routing
weights** — the dominant cell fills, tapers, and therefore stops
accruing weight. The abstract model has no such feedback. Whether γ=1
survives it is a real question with a real answer I do not know in
advance.

## Pre-registration (written before writing the sim, and before any run)

N=20 cells, β=0.05, α=1, F=1, capacity=1, load rate λ=1, I_cap=0.5.
Weight deposit is proportional to **accepted** (not allocated) current —
that is where the physics enters the structural dynamics.

**P1 (threshold survives):** the concentration transition stays at
γ = 1.0, measured within ±0.1, i.e. the measured 50%-transition point
falls in [0.9, 1.1]. Reasoning: L4 established that it is a **uniform**
flow admixture that moves the threshold (γ\*=1/(1−m)); the redistribution
here is weight-**proportional**, not uniform, so it should inject no
uniform component and should therefore behave like L5's cap — setting
depth, not threshold.
**Kill condition for P1:** measured threshold outside [0.9, 1.1]. That
would mean a domain passing *both* structural checks in
`DOMAIN_MAPPING.md` still fails to transfer — a mapping failure of the
same class as ACO's, and evidence the two checks are insufficient.

**P2 (saturation sets a depth floor, L5-style):** even deep in the
monopoly regime (γ=1.6), no true monopoly forms: N_eff stays strictly
above 1, because a monopolist cell self-consistently absorbs only
A = I_cap/(1+I_cap) = 1/3 of total flow and the remaining 2/3 must go
elsewhere. **Kill:** N_eff/N reaching the 1/N monopoly floor.

**P3 (regression control):** with taper disabled (I_cap = ∞), the same
harness must reproduce the abstract threshold at γ=1.0. This detects a
buggy harness, and is explicitly *not* evidence for anything else — it
is the vacuous version of the test, included only as a control.

**Result:** `t6_microgrid.py`, γ sweep 0.6→1.6 at 0.1 resolution, 3 seeds.

| γ | N_eff (control, no taper) | N_eff (physical, taper on) |
|---|---|---|
| 0.6–1.0 | 20.00 | 20.00 |
| 1.10 | 19.55 | 19.55 |
| 1.20 | 1.01 | 3.20 |
| 1.30–1.60 | 1.00 | 3.00 |

**P1 — FAILED AS WRITTEN.** Measured threshold 1.149, outside the
pre-registered [0.9, 1.1] window. I am recording this as a failure
because that is what the pre-registration says, and the whole point of
writing kill conditions in advance is to be bound by them when they
bite.

**But the control failed identically — 1.149, the same number to three
decimals.** The control contains no physics at all; it is the pure
abstract model whose threshold is *analytically known* to be exactly 1
(L1). So a 1.149 reading from the control is not a fact about
microgrids — it is a measurement of my instrument's bias: a 0.1-wide
sweep grid combined with finite runtime and critical slowing near γ=1
(L3 predicts precisely this — near-threshold convergence gets
arbitrarily slow, so a finite run reads the threshold late). My
pre-registered window was tighter than the resolution of the
measurement I chose to make. That is a design error in the
pre-registration, not a discovery about the domain.

**The substantive finding, labelled honestly as POST-HOC** (I did not
pre-register this comparison, and it must not be counted as if I had):
control and physical thresholds are *identical* (1.149 vs 1.149), while
their **depths differ sharply** (floor N_eff = 1.00 vs 3.00). Adding
real charging physics — SOC state, CV taper, refusal, redistribution,
load draw — moved the transition point by nothing measurable and
changed only how deep the concentration goes. That is exactly L5's
signature (caps set depth, not threshold), now reproduced in a system
whose dynamics are not the abstract model's.

**P2 — PASSED.** Floor N_eff = 3.00, far above the monopoly floor of
1.00. No true monopoly forms: physical saturation prevents it.

**P3 — FAILED as written**, same 1.149, same reason; served its purpose
by exposing the instrument bias rather than a harness bug.

## T6b pre-registration — the exact floor law (written before running)

P2's floor landed on **exactly 3.00**, and that is not arbitrary. A
saturated cell self-consistently absorbs A = I_cap/(1+I_cap) of total
flow (accept = I_cap·(1−SOC) with SOC = accept at load equilibrium).
If the locked state consists of cells each pinned at that absorption,
their number — and hence N_eff — should be the reciprocal:

    **N_eff_floor = (1 + I_cap) / I_cap**

At I_cap = 0.5 this gives exactly 3.00, matching the observed floor.
This is a derivation, not a fit, so it makes sharp predictions
elsewhere:

| I_cap | predicted floor |
|---|---|
| 0.10 | 11.00 |
| 0.25 | 5.00 |
| 1.00 | 2.00 |
| 2.00 | 1.50 |

**Kill condition:** any measured floor deviating from its prediction by
more than 5% falsifies the law. (Measured at γ=1.6, deep in the locked
regime, 2 seeds.)

## T6c pre-registration — threshold convergence (written before running)

If 1.149 is finite-time critical slowing rather than a real shift, then
lengthening the run must move the measured threshold **down toward 1.0**
in *both* arms. Prediction: at T=4000 (4× longer) with a 0.05-resolution
grid, both measured thresholds fall below 1.149, and the control's falls
to ≤1.10. **Kill:** thresholds unchanged or rising with longer runtime —
that would mean 1.149 is a genuine property of the system and L1 does
not transfer, reopening P1 as a real failure rather than an instrument
artifact.

**T6b result — FAILED (falsified as written).**

| I_cap | predicted (1+I_cap)/I_cap | measured | rel err |
|---|---|---|---|
| 0.10 | 11.00 | 11.00 | 0.0% |
| 0.25 | 5.00 | 5.00 | 0.0% |
| 0.50 | 3.00 | 3.00 | 0.0% |
| 1.00 | 2.00 | 2.00 | 0.0% |
| 2.00 | 1.50 | **1.80** | **20.0%** |

Four points exact to the displayed precision, one point off by 20% —
over the 5% kill bar, so the law as stated is **falsified**. Recorded as
a failure.

Diagnosis (and note *where* it broke): the four exact points are
precisely those where (1+I_cap)/I_cap is an **integer** (11, 5, 3, 2).
The failure is at I_cap=2.0, the only tested value where it is not
(1.5). My derivation implicitly assumed the locked state is composed of
k identical cells each absorbing A = I_cap/(1+I_cap) with k = 1/A —
which is only coherent when 1/A is a whole number. Cells are discrete;
you cannot have 1.5 of them.

## T6d pre-registration — discreteness-corrected floor law (repair #1)

Correcting the derivation rather than the formula: at the locked state,
k = floor(1/A) cells saturate at absorption A, and the remainder
r = 1 − k·A goes to one further cell. Since weights are proportional to
absorbed current, shares are k copies of A plus one of r, giving

    **N_eff_floor = 1 / (k·A² + r²),  A = I_cap/(1+I_cap),
                    k = floor(1/A),   r = 1 − k·A**

This reduces exactly to the old law when 1/A is an integer (r=0), which
is why those four points matched. Checking it against the datum that
falsified the old law: I_cap=2 → A=2/3, k=1, r=1/3 →
N_eff = 1/(4/9 + 1/9) = **1.80**, the measured value exactly.

That retrodiction is *not* evidence — it is the datum the repair was
built from, and the handoff's retrodiction warning applies in full. The
test is therefore on **five fresh I_cap values never simulated**, chosen
to span both integer and non-integer cases so the law must predict its
own successes *and* its own former failure mode:

| I_cap | k | r | predicted N_eff |
|---|---|---|---|
| 0.20 | 6 | 0 | 6.000 |
| 0.40 | 3 | 1/7 | 3.769 |
| 0.75 | 2 | 1/7 | 2.579 |
| 1.50 | 1 | 0.4 | 1.923 |
| 3.00 | 1 | 0.25 | 1.600 |

**Kill condition:** any of the five deviating by more than 2% falsifies
the repair. Under the carried stopping rule, a second failed repair on
this tier ends work on the floor law entirely — no third attempt.

**T6d result:** _pending._

**T6c result:** _pending (running)._

---
