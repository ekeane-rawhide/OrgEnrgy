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
