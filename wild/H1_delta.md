# H1 — The Delta Substrate: computation without states (spec)

## Axioms

1. **States do not exist.** The only physical primitives are
   **differences**: an atom is δ(a, b), "the difference that takes a to
   b," where a, b range over an abstract site set V. Neither a nor b is
   ever observable alone — a site is only ever seen as an endpoint of a
   difference. A "bit" is a degenerate frozen difference, the way a
   rectangle is a degenerate ellipse.
2. **Composition.** Two differences sharing an endpoint may be fused:
   δ(a, b) ⊕ δ(b, c) → δ(a, c). Fusion CONSUMES both inputs (they cease
   to exist) and produces exactly one output.
3. **Destructive read.** Observing a difference (asking "does this δ
   connect a to b?") consumes it, like a gradient discharging through the
   meter that measures it.
4. **No cloning.** There is no operation producing two differences from
   one. This is not a rule imposed on top of the substrate; it is the
   absence of any primitive that could do it.
5. **Inversion.** δ(a, b) may be flipped in place to δ(b, a) (free).
6. **Genesis.** New differences can only be minted at a distinguished
   boundary ("the source"), never in the interior.

## Claims to test

- C1 (single-use): once read or fused, a difference cannot be used again;
  any attempt is a substrate-level fault, not a policy violation.
- C2 (provenance): a chain δ(a,b) ⊕ δ(b,c) ⊕ δ(c,d) fuses to δ(a,d), and
  the endpoints of every extant difference always trace back to genesis
  events — history is carried in the algebra, not logged beside it.
- C3 (no fan-out ⇒ sub-universality): any Boolean circuit that uses one
  input in two places is unimplementable, because feeding a value to two
  consumers requires cloning. Hence the substrate cannot express general
  Boolean computation; it computes only linear (single-use-per-input)
  dataflows.

## Predicted new capability if it survived

Un-fakeable single-use tokens and tamper-evident provenance *without
cryptography* — enforced by the physics of the substrate rather than by
mathematical hardness assumptions.

## What would kill it

Equivalence to existing named mathematics or an existing computing/
resource-logic paradigm; internal inconsistency in ⊕; or the capability
claims turning out to be restatements of the axioms rather than tests.
