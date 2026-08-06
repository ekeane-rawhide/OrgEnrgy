"""
H2 sim: coincidence-only temporal substrate.

Primitives: coincidence gate (AND-like on timing), first-arrival junction
(OR-like), fixed delay. Encoding: 1 = early pulse, 0 = late pulse.
Tests C1 (AND), C2 (OR) exhaustively, and C3 (NOT impossible) by
exhaustive search over all circuits up to depth 3 on one input plus a
reference pulse.
"""
import itertools

EPS = 0.1        # coincidence window
D = 0.05         # gate output delay
T_EARLY = 0.0
T_LATE = 1.0     # >> EPS
NONE = None      # no pulse


def coincidence(t1, t2):
    if t1 is NONE or t2 is NONE:
        return NONE
    return max(t1, t2) + D if abs(t1 - t2) <= EPS else NONE


def junction(t1, t2):
    if t1 is NONE:
        return t2
    if t2 is NONE:
        return t1
    return min(t1, t2)


def delay(t, dt):
    return NONE if t is NONE else t + dt


def decode(t, t_early_ref):
    """Classify an output pulse as 1 (near early ref) or 0 (near late ref)."""
    if t is NONE:
        return NONE
    return 1 if abs(t - t_early_ref) < 0.5 * (T_LATE - T_EARLY) else 0


def encode(bit):
    return T_EARLY if bit else T_LATE


def test_and():
    # AND: coincidence of the two lines after aligning the "late" slot:
    # a pulse pair coincides iff both are early or both are late; both-late
    # must decode as 0, so take coincidence at each slot separately:
    # AND = junction( coincidence(x, y),                      # both early -> early out
    #                 delay(coincidence(delay(x,-0),..) ) )
    # Simplest correct construction: coincidence(x, y) fires early iff
    # x=y=1, fires late iff x=y=0, silent if they differ. Silent must
    # decode as 0: add a guaranteed late "default" pulse via junction with
    # a reference late pulse.
    ok = True
    for x, y in itertools.product([0, 1], repeat=2):
        c = coincidence(encode(x), encode(y))
        out = junction(c, T_LATE + D)      # late default keeps silence = 0
        got = decode(out, T_EARLY + D)
        want = x & y
        ok &= (got == want)
        print(f"  AND({x},{y}) -> {got} (want {want})")
    return ok


def test_or():
    ok = True
    for x, y in itertools.product([0, 1], repeat=2):
        out = junction(encode(x), encode(y))   # first arrival
        got = decode(out, T_EARLY)
        want = x | y
        ok &= (got == want)
        print(f"  OR({x},{y}) -> {got} (want {want})")
    return ok


def test_not_impossible(max_depth=3):
    """Exhaustive search: single input line x plus reference pulses at
    T_EARLY and T_LATE, all circuits up to max_depth compositions of the
    three primitives. NOT requires out(x=1) decoded 0 and out(x=0)
    decoded 1. Monotonicity argument says no circuit can do it; verify by
    brute force on this finite family."""
    delays = [0.0, D, T_LATE - T_EARLY]

    def signals_at(x):
        return [encode(x), T_EARLY, T_LATE]   # input + both references

    # breadth-first closure of reachable (val_when_x0, val_when_x1) pairs
    pairs = {(s0, s1) for s0, s1 in zip(signals_at(0), signals_at(1))}
    for _ in range(max_depth):
        new = set(pairs)
        for (a0, a1), (b0, b1) in itertools.product(pairs, repeat=2):
            new.add((coincidence(a0, b0), coincidence(a1, b1)))
            new.add((junction(a0, b0), junction(a1, b1)))
        for (a0, a1) in pairs:
            for dt in delays:
                new.add((delay(a0, dt), delay(a1, dt)))
        pairs = new

    for (v0, v1) in pairs:
        if decode(v0, T_EARLY) == 1 and decode(v1, T_EARLY) == 0:
            # found a circuit computing NOT — monotonicity claim falsified
            return False, (v0, v1)
    return True, len(pairs)


if __name__ == "__main__":
    print("C1: AND")
    and_ok = test_and()
    print("C2: OR")
    or_ok = test_or()
    print("C3: NOT impossibility (exhaustive, depth<=3)")
    not_impossible, info = test_not_impossible()
    print(f"  no NOT circuit found among reachable signal pairs: {not_impossible} ({info} pairs searched)")
    print(f"\nC1 {'PASS' if and_ok else 'FAIL'} | C2 {'PASS' if or_ok else 'FAIL'} | "
          f"C3 {'PASS (sub-universal as predicted)' if not_impossible else 'FAIL (NOT found!)'}")
