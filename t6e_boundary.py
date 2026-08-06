"""
T6e: L7 predicts the adversary's counterexample.

Setting L7's floor equal to N gives a regime boundary I_cap* = 1/(N-1).
Above it, concentration proceeds and the floor is L7's value; below it,
the floor exceeds N and concentration is impossible. Pre-registered in
LEDGER.md before this file was run.
"""
import numpy as np
from t6_microgrid import run, N


def l7_floor(i_cap):
    a = i_cap / (1.0 + i_cap)
    k = int(np.floor(1.0 / a))
    r = 1.0 - k * a
    return 1.0 / (k * a * a + r * r)


if __name__ == "__main__":
    boundary = 1.0 / (N - 1)
    print(f"L7 regime boundary: I_cap* = 1/(N-1) = {boundary:.4f}\n")
    print(f"{'I_cap':>7} {'L7 floor':>9} {'predicted':>10} {'measured':>10} {'rel err':>9}  verdict")
    worst, ok = 0.0, True
    for i_cap in [0.04, 0.05, 0.06, 0.08]:
        floor = l7_floor(i_cap)
        predicted = min(floor, float(N))       # a floor above N is unreachable
        measured = float(np.mean([run(1.6, i_cap=i_cap, seed=s, t_total=4000.0)[0]
                                  for s in (0, 1)]))
        rel = abs(measured - predicted) / predicted
        worst = max(worst, rel)
        side = "below boundary" if i_cap < boundary else "above boundary"
        print(f"{i_cap:7.3f} {floor:9.2f} {predicted:10.2f} {measured:10.2f} "
              f"{rel:8.2%}  {'ok' if rel <= 0.03 else 'DEVIATES'}  ({side})")
    print(f"\nT6e worst relative error: {worst:.2%} -> "
          f"{'PASS (L7 predicts the counterexample and the boundary)' if worst <= 0.03 else 'FAIL'}")
