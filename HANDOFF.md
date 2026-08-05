# HANDOFF — Deposition/Decay/Routing Universality (prior session)

Carried over verbatim for reference by the current session's ledger. This
session's own work starts in `LEDGER.md`; this file is read-only history.

## Model

    dC_i/dt = α·F · C_i^γ / Σ_j C_j^γ − β·C_i

C_i = channel strength, α = deposition rate, β = decay rate, F = total flow,
γ = routing exponent. S=ΣC_i obeys dS/dt = αF − βS, so S* = αF/β independent
of γ. At x_i = C_i/S*: dx_i/dt = β(x_i^γ/Σx_j^γ − x_i). γ carries all the
geometry; β is only a timescale.

## Verified laws

- **L1**: critical point at γ=1 (eigenvalue β(γ−1) about uniform state).
  Distributed for γ<1, monopoly for γ>1. Confirmed to 3e-4, γ∈[0.4,1.8], N=20.
- **L2**: γ=1 is a zero eigenvalue → neutral drift → any finite stochastic
  system fixates. Stable interval is half-open: distributed γ<1, monopoly
  γ∈[1,∞).
- **L3**: threshold invariant in N (10/50/200 all confirm); near-threshold
  degradation grows with N (critical slowing, the real signature of
  criticality).
- **L4**: uniform-flow admixture m shifts threshold to γ* = 1/(1−m). Routing
  p_i = (1−m)x_i^γ/Σx^γ + m/N, eigenvalue β[(1−m)γ−1]. Confirmed for
  m=0/0.1/0.2 (collapse at 1.0/1.1/1.25); m=0.3 fixates early per L2.
- **L5**: per-channel inflow cap c sets the locked-state floor at exactly
  1/(N·c), not the threshold — threshold stays 1.0–1.2 for every c tested.

## Failed domain mapping (ACO)

- **F1**: ACO threshold measured at 1.30, not 1.00. Structural cause: TSP
  tour feasibility removes edges from the pool as the tour is built (a
  shrinking-candidate-set, per-node topology), whereas the abstract model
  assumes one shared global normalization pool. This is a **mapping error**,
  not a model error — the model wasn't wrong, ACO just isn't the right shape
  of system for it.
- **F2**: repair "capacity saturation" (inflow cap) — falsified by L5: caps
  set depth, not threshold.
- **F3**: repair "forced exploration as uniform-flow admixture m" — the
  abstract check (does L4's γ*=1/(1−m) reproduce in the abstract model)
  passed, but the independent in-ACO measurement of m predicted γ*=1.836 vs
  observed 1.30 — outside the pre-registered kill window. The one available
  rescue makes the estimator unfalsifiable (it can hit any target in the
  measured range) — halt signal, not confirmation.

**Stopping rule**: two failed repairs on a tier → halt. Triggered here.
Unexecuted: T4 (second domain sharing the model's shared-pool topology), T5
(cross-domain collapse test, the actual universality claim), T6 (never
started — β* sketch is not a result, do not cite it).

## Method discipline (binding on this session too)

1. Write the numeric prediction before the run.
2. State the kill condition in the same breath.
3. Cheapest-kill-first ordering.
4. On failure: distinguish model error from mapping error.
5. Two failed repairs on one tier → halt.
6. A clean falsification beats an unfinished collapse test.

Retrodiction warning carried forward: constructing a domain mapping *after*
knowing the answer you want (as with the original TCP/Hebbian/river/ACO
readings) is not evidence. Pre-register before running, always.
