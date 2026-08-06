"""
H5: an operational severity observable.

    S = relative change in a test's measured quantity when the mechanism
        the hypothesis holds responsible is toggled or swept.

S ~ 0  -> mechanism inert in the tested regime -> verdict fixed by
          construction -> VACUOUS
S large -> verdict tracks the mechanism -> SEVERE

Scored against six tests from this session whose vacuous/severe status
was established independently by adversarial review. The labels are NOT
given to the estimator; they appear only at the end for scoring.
"""
import sys, os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def severity(measure, settings):
    """measure: callable(setting) -> float, the quantity the test reads.
    settings: the mechanism toggled/swept across its meaningful range.
    S = relative spread of the measured quantity across that sweep."""
    vals = np.array([float(measure(s)) for s in settings], dtype=float)
    scale = np.max(np.abs(vals))
    if scale < 1e-15:
        return 0.0
    return float((vals.max() - vals.min()) / scale)


# ---------------------------------------------------------------- cases
def case_h1_fanout():
    """H1's fan-out test. Mechanism: whether the substrate permits
    cloning. Toggle it and see if the test's verdict moves."""
    from h1_sim import Substrate, test_c3_no_fanout, Delta

    def measure(allow_cloning):
        s = Substrate()
        if allow_cloning:
            # a substrate that DOES permit copying -- C3 should now fail
            def clone(self, d):
                return Delta(d.a, d.b, parents=(d,), genesis=d.genesis)
            Substrate.clone = clone
        try:
            return 1.0 if test_c3_no_fanout(s) else 0.0
        finally:
            if hasattr(Substrate, "clone"):
                del Substrate.clone

    return severity(measure, [False, True])


def case_h2_and():
    """H2's AND test. Mechanism: the input values. A real truth table
    must produce different outputs for different inputs."""
    from h2_sim import coincidence, junction, encode, decode, T_EARLY, T_LATE, D

    def measure(inputs):
        x, y = inputs
        out = junction(coincidence(encode(x), encode(y)), T_LATE + D)
        return float(decode(out, T_EARLY + D))

    return severity(measure, [(0, 0), (0, 1), (1, 0), (1, 1)])


def case_t4_p1():
    """T4's P1. Mechanism claimed responsible: the acceptance taper.
    Toggle the taper across the pre-registered kill window [0.9, 1.1]."""
    from t6_microgrid import run

    def measure(i_cap):
        return np.mean([run(g, i_cap=i_cap, seed=0, t_total=400.0)[0]
                        for g in (0.9, 1.0, 1.1)])

    return severity(measure, [np.inf, 0.5])


def case_h4_c2():
    """H4's C2. Mechanism claimed responsible: the diffusive medium.
    Toggle diffusion at the value the headline table actually used."""
    from h4_sim import run

    def measure(D):
        return run(0.25, D=D, seed=0, t_total=400.0)[1]

    return severity(measure, [0.0, 1e-4])


def case_t6d_l7():
    """T6d. Mechanism claimed responsible: the per-cell cap setting the
    floor. Sweep the cap across its meaningful range."""
    from t6_microgrid import run

    def measure(i_cap):
        return run(1.6, i_cap=i_cap, seed=0, t_total=600.0)[0]

    return severity(measure, [0.10, 0.25, 0.50, 1.00])


def case_t6e_boundary():
    """T6e. Mechanism: the cap, swept across the predicted regime
    boundary at I_cap* = 1/(N-1)."""
    from t6_microgrid import run

    def measure(i_cap):
        return run(1.6, i_cap=i_cap, seed=0, t_total=600.0)[0]

    return severity(measure, [0.04, 0.06, 0.08])


if __name__ == "__main__":
    cases = [
        ("H1 test_c3_no_fanout", case_h1_fanout),
        ("H2 test_and",          case_h2_and),
        ("T4 P1 threshold",      case_t4_p1),
        ("H4 C2 individuation",  case_h4_c2),
        ("T6d L7 fresh points",  case_t6d_l7),
        ("T6e boundary",         case_t6e_boundary),
    ]
    # labels revealed only for scoring, never used by severity()
    labels = {"H1 test_c3_no_fanout": "VACUOUS", "T4 P1 threshold": "VACUOUS",
              "H4 C2 individuation": "VACUOUS", "H2 test_and": "SEVERE",
              "T6d L7 fresh points": "SEVERE", "T6e boundary": "SEVERE"}

    print(f"{'test':>22} {'S':>8}  {'instrument says':>15}  {'true label':>10}")
    results = {}
    for name, fn in cases:
        s = fn()
        verdict = "VACUOUS" if s < 0.05 else ("SEVERE" if s > 0.5 else "AMBIGUOUS")
        results[name] = (s, verdict)
        mark = "ok" if verdict == labels[name] else "MISCLASSIFIED"
        print(f"{name:>22} {s:8.4f}  {verdict:>15}  {labels[name]:>10}  {mark}")

    vac = [s for n, (s, _) in results.items() if labels[n] == "VACUOUS"]
    sev = [s for n, (s, _) in results.items() if labels[n] == "SEVERE"]
    print(f"\nP1 all vacuous S < 0.05:  {max(vac):.4f} -> {'PASS' if max(vac) < 0.05 else 'FAIL'}")
    print(f"P2 all severe  S > 0.50:  {min(sev):.4f} -> {'PASS' if min(sev) > 0.50 else 'FAIL'}")
    print(f"P3 clean separation:      gap {min(sev) - max(vac):+.4f} -> "
          f"{'PASS' if min(sev) > max(vac) else 'FAIL'}")
    miss = [n for n, (s, v) in results.items() if v != labels[n]]
    print(f"misclassifications: {miss if miss else 'none'}")
