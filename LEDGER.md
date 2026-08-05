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
