# H3 — The Rented-Memory Machine: metabolism as computation (spec)

## Axioms

1. **Nothing is stored.** Every persistent quantity is *paid for* by
   recurring flow. A value exists exactly as long as it is re-derived;
   stop paying and it decays at rate β.
2. The machine's memory is a set of scores C_i. Each access to item i
   deposits α onto C_i; every step, all scores decay: C ← (1−β)C.
3. The machine's working set is whatever currently ranks in its top-N
   scores. There is no eviction policy — eviction IS decay.
4. Forgetting is therefore free and automatic; attention (sustained
   flow) is the only thing that keeps a memory alive. The "program" is a
   flow allocation, not an instruction sequence.

## Claims to test

- C1: under a drifting workload (the item distribution re-permutes
  periodically), the rented machine's next-item hit-rate recovers after
  each drift event, and beats an exact-count LFU baseline of identical
  budget (prediction: ≥5-point hit-rate gap after the first drift).
- C2 (the honest self-test): the closed form of the score is
  C_i(t) = α Σ_s (1−β)^(t−s) · [i accessed at s] — check numerically
  that the substrate's scores exactly match this expression. If they do,
  the substrate is an exponential moving average of access flow and the
  "new machine" framing must be downgraded accordingly.

## Predicted new capability if it survived

A machine that cannot suffer stale state: importance-weighted forgetting
with zero bookkeeping, no eviction logic, no TTLs.

## What would kill it

C2 confirming the EMA reduction (expected), equivalence to existing
decayed-frequency schemes, or the capability advantage in C1 failing to
materialize.
