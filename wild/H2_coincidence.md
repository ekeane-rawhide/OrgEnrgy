# H2 — Coincidence-Only Substrate (spec)

## Axioms

1. The only physical objects are **pulses**: identical, indistinguishable
   events. A pulse carries no payload. All information lives in *when* a
   pulse occurs relative to other pulses.
2. The only primitive operation is the **coincidence gate**: given two
   input lines, emit one output pulse at time `max(t1, t2) + d` iff
   `|t1 − t2| ≤ ε` (both pulses arrive within the coincidence window).
   Otherwise emit nothing.
3. A **junction** merges two lines: the output carries whichever pulse
   arrives first (`min(t1, t2)`), the later one is absorbed.
4. Fixed **delay lines** (`t → t + δ`) are free.
5. No inhibition: a pulse can never *prevent* another pulse. No payloads,
   no amplitudes, no refractory tricks.

## Encoding

Temporal binary: on each line, logical 1 = pulse at reference time T_early,
logical 0 = pulse at T_late = T_early + Δ, with Δ ≫ ε.

## Claims to test

- C1: AND is implementable (coincidence-family construction using max).
- C2: OR is implementable (junction = min).
- C3 (the load-bearing one): NOT is **impossible** in this substrate.
  Argument to check: every primitive (max+d, min, +δ) is a *monotone*
  function of arrival times — earlier inputs can never produce a strictly
  later output pattern. NOT requires anti-monotonicity (early in → late
  out). A composition of monotone functions is monotone, so no circuit
  built from these primitives computes NOT. Hence the substrate is
  sub-universal (monotone Boolean functions only) without adding an
  inhibitory primitive.

## Predicted capability if it survived

Clockless, payload-free logic where energy per operation is one pulse.

## What would kill it

Equivalence to an existing computing paradigm, or failure of C1/C2, or a
counterexample to C3's monotonicity argument.
