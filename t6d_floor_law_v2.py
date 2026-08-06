"""
T6d: discreteness-corrected floor law (repair #1 of T6b).

    N_eff_floor = 1 / (k*A^2 + r^2),  A = I_cap/(1+I_cap),
                  k = floor(1/A),     r = 1 - k*A

Tested on five FRESH I_cap values never previously simulated, spanning
both integer and non-integer 1/A. Predictions pre-registered in
LEDGER.md before this file was run.
"""
import numpy as np
from t6_microgrid import run


def predict(i_cap):
    a = i_cap / (1.0 + i_cap)
    k = int(np.floor(1.0 / a))
    r = 1.0 - k * a
    return 1.0 / (k * a * a + r * r), k, r, a


if __name__ == "__main__":
    print("T6d: discreteness-corrected floor law, five fresh I_cap values")
    print(f"{'I_cap':>7} {'k':>3} {'r':>7} {'predicted':>10} {'measured':>10} {'rel err':>9}  verdict")
    worst = 0.0
    for i_cap in [0.20, 0.40, 0.75, 1.50, 3.00]:
        p, k, r, a = predict(i_cap)
        vals = [run(1.6, i_cap=i_cap, seed=s)[0] for s in (0, 1)]
        measured = float(np.mean(vals))
        rel = abs(measured - p) / p
        worst = max(worst, rel)
        print(f"{i_cap:7.2f} {k:3d} {r:7.4f} {p:10.3f} {measured:10.3f} "
              f"{rel:8.2%}  {'ok' if rel <= 0.02 else 'DEVIATES'}")
    print(f"\nT6d worst relative error: {worst:.2%} -> "
          f"{'PASS (corrected law holds within 2%)' if worst <= 0.02 else 'FAIL (repair #1 falsified)'}")
