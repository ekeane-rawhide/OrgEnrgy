# Step 4 — domain mapping check (static, before any domain sim is built)

Two independent structural checks, both must pass before a domain
simulation is worth building. ACO (prior session) failed check A. This
session's L6 result adds check B, which nothing in the prior session
tested for.

**Check A — shared competition pool.** All channels must normalize
against the same Σ_j C_j (or Σ_j f(C_j)) at every step — not a per-node
view over a private, shrinking candidate set. This is the structural
reason ACO failed to map (tour-feasibility removes edges from the pool as
each tour is built).

**Check B — power-law kernel (L6, this session).** The domain's actual
allocation rule must be (or be well-approximated by) a true power law
f(C_i) ∝ C_i^γ. If it's instead exponential/softmax/sigmoid, the critical
point is not γ=1 and is not N-invariant — L1–L5 don't transfer as-is, only
the more general (and less "universal-sounding") elasticity relation from
L6 does.

## Candidates evaluated

| Domain | Check A (shared pool) | Check B (power-law kernel) | Verdict |
|---|---|---|---|
| Diode-OR harvester swarm into shared storage bus (physical circuit; higher-voltage source wins disproportionate current) | **Pass** — one shared bus | **Fail** — diode I-V is exponential (Shockley), so the natural kernel is f(x)=exp(x/V_th)-like, not a power law. L6 predicts a size-dependent critical "temperature" T\*=1/N, not a fixed γ\*=1 | Wrong shape of test for L1–L5; would need the L6 curve, not the γ=1 line, as the validation target |
| Software-defined microgrid charge controller: N storage cells on a shared DC bus, controller explicitly allocates incoming charge current as C_i^γ/Σ_j C_j^γ, self-discharge as decay | **Pass** — one controller, one shared allocation budget | **Pass by construction** — the exponent is a literal tunable parameter in the control law, not something inferred from physics | **Best candidate.** This is not a pre-existing physical system whose kernel has to be discovered/estimated (the estimator problem in handoff §5C) — it's a control law we specify, so both checks pass exactly, by design, not by hopeful approximation |
| TinyLFU-style cache admission with frequency-weighted competition for a fixed admission budget | **Pass** — one shared admission budget per epoch | **Depends on implementation** — real TinyLFU uses roughly linear (count-based) weighting; would need to deliberately raise the weight to a tunable power to get a true power-law kernel, same as the microgrid case | Viable second domain, same caveat as above: only passes Check B if the exponent is designed in, not discovered |
| Nonlinear preferential-attachment network growth (edges added ∝ degree^γ) with edge decay | **Pass** — one shared pool (all nodes compete for the same new edge) | **Pass by construction** — γ is literally the model's parameter | Valid candidate, **and already has an existing literature result**: Krapivsky & Redner's work on nonlinear preferential attachment (see note below) independently derives a transition at γ=1 between a stationary power-law degree distribution (γ=1) and "gelation"/winner-take-all condensation (γ>1) — structurally the same finding as L1, obtained from an entirely different formalism (rate equations for degree distributions, not the C_i replicator ODE used here) |

## Important honesty note on L1 vs prior literature

The nonlinear preferential-attachment literature (Krapivsky, Redner, and
collaborators, ~2000) already documents a γ=1 phase transition of this
same qualitative shape (distributed/power-law below, condensation/gel
above) for network growth specifically. This session did not verify that
literature result directly — it's cited from background knowledge, not
re-derived here, so it should be treated as *background context to check
independently*, not as confirmed evidence. But it changes how L1 should be
framed going forward: **if it holds up, L1 is a rediscovery of a known
result in one specific domain (network growth), not a novel finding** —
what would still be novel, and still untested, is that the *same*
transition governs domains as different as microgrid charge allocation,
cache admission, and network growth via one shared abstract mechanism.
That's the actual universality claim (handoff's T5, never executed), and
this literature connection is a reason *for* pursuing it, not evidence
against — an independently-known result in one domain is exactly the kind
of anchor a cross-domain collapse test needs.

## Recommendation

Build the **software-defined microgrid controller** as the T4 domain: it
passes both checks by construction rather than by hopeful approximation,
it directly instantiates this session's "new form of energy harnessing"
proposal (self-tuning-criticality control law) as a concrete system rather
than a purely abstract exercise, and it sidesteps the estimator problem
(handoff §5C) since the exponent is a design parameter, not something that
has to be inferred from noisy real data.

**Not done in this session** — scoped as the next actionable step, now
that the domain has been chosen for a stated, checked reason rather than
by the retrodiction pattern the handoff warned against:
- Build the T4 simulation, pre-register the predicted threshold (γ=1,
  N-invariant, per L1/L3, since Check B passes by construction) *before*
  running it.
- If it holds, this becomes the first real (not just abstract) validation
  of the deposition/decay/routing model, satisfying the never-executed
  handoff item A.
- The nonlinear-PA literature connection should be checked against actual
  papers before being repeated as settled fact anywhere outside this note.
