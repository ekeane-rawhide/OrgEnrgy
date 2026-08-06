# Wild Hypothesis Foundry — Final Verdict

## The brief

Generate hypotheses from pure instinct, no literature input, aimed past
existing technology — then have independent adversarial agents try to
kill each one, where "this already exists under another name" counts as
a kill. Three hypotheses entered. The kill process was itself calibrated
by planting one deliberately-killable hypothesis (H2) and requiring the
adversaries to execute it before any other verdict counted.

## Results

| Hypothesis | Sim result | Adversary verdict | Named prior art it turned out to be |
|---|---|---|---|
| **H1 — Delta Substrate** (computation without states; only differences exist, uncopyable, destructively read) | All 3 claims passed | **KILLED(reduction)** | Groupoids (Brandt 1927) + linear logic (Girard 1987) + the no-cloning theorem (Wootters & Zurek 1982) + Wiesner's quantum money (~1970) + Petri nets (1962); the sub-universality "prediction" is why Girard invented the `!` modality |
| **H2 — Coincidence-only substrate** (calibration corpse) | All 3 claims passed | **KILLED(reduction)** — gate passed | Race Logic (ISCA 2016), 1950s diode logic, tropical (min,+)/(max,+) semirings, monotone circuit theory (Razborov et al.) |
| **H3 — Rented-Memory Machine** (nothing stored, memory paid for by flow) | Capability test passed, own self-test confirmed EMA reduction at 7e-15 | **KILLED(reduction)** | LRFU caching (Lee et al. 1999), TD(λ) eligibility traces (Sutton & Barto), EWMA/Jacobson estimator, Redis/Squid/Caffeine aging counters |

Three for three. Every kill matched the pre-registered prediction of
*which* prior art would surface — recorded in `../LEDGER.md` before the
adversaries ran, and never shown to them.

The adversaries additionally found **four flaws I did not plant**:
1. H2's spec asserted a monotonicity theorem that is false as stated
   (true only on the restricted encoding domain the sim used).
2. H2's "exhaustive" impossibility search was scoped narrowly enough to
   be confirmation-only.
3. H3's baseline (never-decaying LFU) was a strawman — every deployed
   LFU variant includes decay precisely because pure counting is
   known-pathological under drift, so most of the reported +7.7-point
   advantage was an artifact of the opponent, not a capability.
4. H1's flagship test (`test_c3_no_fanout`) was vacuous: it re-ran the
   C1 test under a new name and asserted a hard-coded True that no
   implementation, correct or broken, could falsify. I wrote it and did
   not notice.

## What this actually measured

The experiment was a fair, fully-executed test of the premise "discard
existing research and hypothesize from raw instinct, and something
beyond current technology may emerge." The measured outcome:

1. **Instinct is trained on the world, and the world already did the
   work.** All three from-scratch ideas — generated with genuine effort
   at strangeness, not sandbagged — landed within one rename of named
   mathematics, most of it 40–100 years old. The delta substrate's
   axioms reproduced, almost clause for clause, the specific combination
   (linear resources + invertibility + destructive measurement +
   no-cloning) that quantum information theory spent decades
   formalizing. That is not a coincidence; it is what "wildly new from
   first principles" converges to when the first principles are real.
2. **The self-testing standard of one mind is not enough.** Four flaws
   survived my own review and pre-registration discipline and were
   caught only by adversaries with no stake in the hypotheses. Two of
   those flaws (the rigged baseline, the vacuous test) are exactly the
   pattern by which "revolutionary" results get published and then fail
   to replicate.
3. **The one thing in this repo that has produced durable results all
   session is the loop, not any hypothesis** — pre-register, state the
   kill, let something hostile attack it, record verbatim. That loop
   killed ACO's mapping, killed two repairs, falsified the adiabatic
   model, killed all three wild substrates, and every one of those
   corpses taught something specific. The loop is the technology.

## What a genuine survivor would have needed next

For completeness, the bar a surviving hypothesis would still have had to
clear before any claim beyond "internally consistent in simulation":
a physical instantiation argument (what medium implements the axioms and
at what energy scale), a capability demonstration against the *strongest*
known incumbent rather than a convenient baseline, and independent
replication from the spec alone. No candidate reached that stage.

## Standing recommendation

The productive frontier in this repository remains the un-run
experiment with a pre-registered prediction: the microgrid domain test
(`../DOMAIN_MAPPING.md`), where the model, the threshold (γ=1,
N-invariant), and the kill condition are already written down and
nothing about it requires a revolution — only a result.
