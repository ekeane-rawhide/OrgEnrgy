# Self-Tuning Criticality: an adaptive-γ control law for energy networks

## The formula

    dC_i/dt = α F · C_i^γ(t) / Σ_j C_j^γ(t) − β C_i
    dγ/dt   = κ ( γ_target(σ_F) − γ )
    γ_target(σ_F) = γ_max − (γ_max − γ_min) · g(σ_F)

An extension of the verified deposition/decay/routing model (see
`HANDOFF.md`): γ, the exponent governing whether flow concentrates or
distributes, is no longer a fixed design parameter. It becomes a slow
state variable that reads a stress/volatility signal σ_F off the network's
own flow and slides toward the distributed regime (γ<1) under stress, the
monopolized regime (γ>1) under calm.

## The philosophy

A fixed γ commits a network to one point on the efficiency/resilience
trade-off forever. Self-tuning criticality treats that commitment as a
mistake: hold the network near its own phase boundary and let local,
cheaply-measured flow statistics — not a central optimizer — decide which
side of it to lean toward, moment to moment. It is a decentralized
alternative to explicit optimal-power-flow control: robustness and
efficiency traded automatically along one dial, driven by information the
network already has.

## What testing it actually found

The value of this session wasn't just proposing the formula — it was
running it hard enough to find where it breaks and whether the breakage
still leaves something useful. Full detail and every pre-registration is
in `LEDGER.md`; summary:

- **The fixed point of γ=1 criticality survives the extension exactly**
  (Step 0): adding slow γ-dynamics doesn't move L1's threshold, for any κ,
  as long as the stress signal is exogenous to the channel state — a
  block-triangular Jacobian argument, not a numerical coincidence.

- **But the naive mental model — "γ slides, structure follows with a
  lag of about 1/κ" — is false** (Step 2, falsified). What actually
  happens is *pinning*: because the system's own relaxation rate vanishes
  exactly at γ=1 (this is L1's eigenvalue going to zero, and L2's neutral
  drift, showing up dynamically now instead of just at steady state),
  structure stays pinned near its old configuration through the entire
  crossing and only starts moving once γ has swept nearly all the way to
  its new target — regardless of how slowly γ was moved. Slower γ doesn't
  fix this; it can't, because the obstruction is a hard zero in the
  relaxation rate, not a mismatched timescale.

- **Despite that, the resilience payoff is real and large** (Step 3,
  after two bugs caught mid-test — a hidden exact symmetry that silently
  prevented any redistribution at all, and a metric that measured the
  wrong thing). Under channel failure, a self-tuning network holds a safe,
  redistributed state roughly **3.1× longer** than a fixed-γ network
  before re-concentrating into a new single point of failure, consistent
  across seeds (3.04–3.20×). The lesson: pinning delay means the response
  isn't instant, but a delayed, partial response still crushes no response
  at all.

- **The clean, N-independent γ=1 threshold is not a generic property of
  "prefer what's already big" competition — it's specific to power-law
  kernels** (L6, a new generalization derived this session). Physical
  winner-take-most mechanisms that arise naturally in circuits — e.g.
  diode-OR arbitration between energy sources sharing a bus, which
  competes roughly exponentially in relative voltage — have a critical
  point that *depends on network size* (derived and confirmed: critical
  "temperature" T\*=1/N). That means a real diode-OR energy-harvester
  swarm is the **wrong** first domain to validate this model against, for
  a structural reason, not a tuning failure — exactly the kind of mistake
  that sank the prior session's ACO test, caught here *before* building
  anything (see `DOMAIN_MAPPING.md`).

## The concrete proposal: a software-defined microgrid controller

Not a new physical transducer — a new **control law** for existing
storage/harvesting hardware, chosen specifically because it's the one
candidate domain that passes both structural checks *by construction*
rather than by hope:

- N storage cells share one DC bus and one allocation budget (shared-pool
  topology — passes the check ACO failed)
- the controller explicitly implements C_i^γ(t)/Σ_j C_j^γ(t) as its
  charge-allocation rule, with γ a literal tunable exponent, not something
  inferred from noisy physics (passes L6's power-law requirement by
  design)
- σ_F is read from the bus's own supply variance / node-failure signal —
  no external optimizer, no forecasting model, no central controller
  beyond this one local rule

Given the pinning-delay finding, this is honestly pitched: not "instant
adaptive resilience," but "a slow dial that, once it starts moving,
delivers a large, measured resilience benefit at a bounded and
now-understood cost in response latency." That's a narrower and more
defensible claim than the philosophy section alone would suggest, and it's
the one the numbers actually support.

## What's next (not done this session, scoped and ready)

Build the microgrid T4 domain simulation itself — this session did the
check that determines *which* domain is worth building (see
`DOMAIN_MAPPING.md`'s recommendation), following through on the actual
build is the next step, pre-registered before running: predicted
threshold γ=1, N-invariant, per L1/L3/L6.
