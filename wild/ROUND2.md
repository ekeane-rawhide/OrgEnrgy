# Wild Hypothesis Foundry — Round 2

## Why Round 1 died (diagnosis, not excuse)

H1 → groupoids + linear logic + no-cloning. H2 → tropical semirings +
race logic. H3 → EWMA + LRFU. Three different-feeling ideas, three
kills, and the kills share a structure:

**All three were compositional substrates.** Each asked the same
question — *what are the atoms, and what is the rule for combining
them?* But that question is the definition of category theory, and
mathematicians have spent a century mapping the space of answers
exhaustively. Any proposal of that shape lands somewhere already named.
Generating "wilder" atoms does not help; the atlas covers the whole
space, not just the tame parts of it.

So the failure was not insufficient imagination. It was **searching in a
completed region**.

## Round 2 generation strategy (changed deliberately)

Propose a system with **no fixed set of parts at all** — where "how many
things exist" is an *output* of the dynamics rather than an input to the
model. If there is no predetermined set of atoms, there is nothing for a
composition rule to be about, and the category-theoretic atlas has no
grip.

This is a real gap in everything in this repository: every model here
(L1–L7, the adaptive-γ work, the microgrid) fixes N in advance. C_i is
indexed by an i that the modeller chose. **Individuation — how the world
gets divided into countable things — is an assumption in all of it,
never a result.**

## H4 — The Individuation Hypothesis

**Axiom.** There are no channels. There is a structureless medium
u(x,t) on a continuous domain, subject to the same deposition/decay/
routing law, plus local diffusion and a per-location acceptance cap:

    ∂u/∂t = F · cap[ u^γ / ∫u^γ ] − β u + D ∇²u

Nothing in this equation names a part, counts a part, or indexes a part.
"How many channels exist" is not a parameter — it is measured from the
resulting field by counting peaks.

**C1 (individuation happens):** discrete, countable structures
precipitate out of the structureless medium from near-uniform initial
conditions, and the resulting count is reproducible across random seeds
rather than being frozen noise.

**C2 (the load-bearing claim): the emergent part-count is predicted by
L7** — a law derived for a system with a *fixed* number of parts. If a
medium with no predetermined parts spontaneously divides itself into
exactly the number L7 specifies, then L7 is describing something more
general than the fixed-N system it was derived on: it predicts how many
things there will be, not just how concentrated a known set becomes.

Predictions (γ=1.6, from L7 with A = I_cap/(1+I_cap)):

| I_cap | A | predicted peaks | predicted N_eff |
|---|---|---|---|
| 0.50 | 1/3 | 3 | 3.00 |
| 0.25 | 1/5 | 5 | 5.00 |
| 0.10 | 1/11 | 11 | 11.00 |

**C3 (count is not a diffusion artifact):** the emergent count is
independent of D over at least a 10× range. D should set peak *width*,
not peak *number* — the cap sets the number. If the count tracks D, the
individuation is just a pattern-formation length-scale and C2 is
coincidence.

**Kill conditions:** peak count off L7 by more than 1; or N_eff off by
>10%; or count varying with D by more than 1 over the tested range; or
counts not reproducible across seeds.

## Meta-pre-registration (the actual experiment about idea generation)

Round 1's kills all came from **algebra** (category theory, logic,
semirings). I predict H4 dies too, but to a **different family**:
pattern formation — nonlocal reaction-diffusion, Turing (1952),
Cahn-Hilliard coarsening, or spike/mesa solutions in nonlocal RD.

That prediction is the point. If H4 dies to pattern formation, the
strategy change *moved the search* into a different region of
idea-space, and "generate differently" is a controllable variable. If it
dies to algebra again, the strategy change did nothing and the problem
is deeper than where I chose to look. If it survives, that is a result
requiring physical follow-up before any claim.

Recorded before running, and not shown to the adversary.

---

# H4 RESULTS

```
 I_cap  L7 pred   peaks(3 seeds)   N_eff   rel err
  0.50     3.00        [2, 3, 3]    3.02      0.7%
  0.25     5.00        [4, 5, 5]    5.04      0.8%
  0.10    11.00      [9, 10, 11]   11.08      0.7%

C3, I_cap=0.25 (L7 predicts 5):
  D=1e-05  peaks= 4   N_eff=5.00
  D=1e-04  peaks= 4   N_eff=5.03
  D=1e-03  peaks= 3   N_eff=5.26
  D=1e-02  peaks= 1   N_eff=5.84
```

**The script printed `PASS`. That verdict is wrong and I am overriding
it.** The script checked only the worst N_eff error against the 10%
bar; my pre-registration listed four kill conditions and several fired.
Scoring against what was actually written:

- **C2 (N_eff matches L7): PASSED, strongly.** 3.02/5.04/11.08 against
  predictions of 3/5/11 — under 1% at every point, and stable.
- **C1 (reproducible counts): marginal FAIL.** At I_cap=0.10 the peak
  count spans [9, 10, 11] across seeds — a spread of 2, over the
  ≤1 bar.
- **C3 (count independent of D): CLEAR FAIL.** Over a 1000× range in D
  the peak count collapses 4 → 4 → 3 → **1**, far outside the ±1 bar.

**So the load-bearing individuation claim fails, and the failure is
informative.** At D=1e-2 the field has *one* local maximum but an N_eff
of 5.84 — the mass is still distributed as L7 says, but it is no longer
organised into discrete countable peaks. The two things come apart:

> **L7 predicts the effective mass distribution robustly. It does not
> predict discrete countability.** Whether the medium's mass is carved
> into separable "things" is set by D — a pattern-formation length
> scale — not by L7.

That is precisely the boundary H4 was built to probe, and the answer is
that individuation is *not* delivered by the deposition/decay law. The
count was smuggled in by the diffusion term all along.

**Vacuity risk I should flag before the adversary does:** at D→0 the
medium is M=128 non-interacting sites, i.e. the fixed-N model with
N=128 wearing a spatial costume — and L7 already predicts N_eff there
regardless of N. So C2's success in the small-D limit may be trivial,
and the honest test of anything new is the D-dependence, which is where
it broke. Going to the adversary now.
