"""
T6b: test the derived floor law  N_eff_floor = (1 + I_cap) / I_cap
T6c: threshold convergence check -- is the 1.149 reading finite-time
     critical slowing (L3) or a real shift?

Both pre-registered in LEDGER.md before this file was run.
"""
import numpy as np
from t6_microgrid import run, threshold_of, sweep, N


def floor_law_test():
    print("T6b: derived floor law  N_eff_floor = (1 + I_cap)/I_cap")
    print(f"{'I_cap':>7} {'predicted':>10} {'measured':>10} {'rel err':>9}  verdict")
    worst = 0.0
    for i_cap in [0.10, 0.25, 0.50, 1.00, 2.00]:
        predicted = (1.0 + i_cap) / i_cap
        vals = [run(1.6, i_cap=i_cap, seed=s)[0] for s in (0, 1)]
        measured = float(np.mean(vals))
        rel = abs(measured - predicted) / predicted
        worst = max(worst, rel)
        print(f"{i_cap:7.2f} {predicted:10.2f} {measured:10.2f} {rel:8.1%}  "
              f"{'ok' if rel <= 0.05 else 'DEVIATES'}")
    print(f"\nT6b worst relative error: {worst:.1%} -> "
          f"{'PASS (law holds within 5%)' if worst <= 0.05 else 'FAIL (law falsified)'}")
    return worst


def convergence_test():
    print("\nT6c: threshold convergence (is 1.149 critical slowing?)")
    gammas = np.round(np.arange(0.90, 1.30, 0.05), 2)
    rows = []
    for t_total, label in [(1000.0, "T=1000 (original)"), (4000.0, "T=4000 (4x)")]:
        ctrl = np.array([np.mean([run(g, i_cap=np.inf, seed=s, t_total=t_total)[0]
                                  for s in (0, 1)]) for g in gammas])
        phys = np.array([np.mean([run(g, i_cap=0.5, seed=s, t_total=t_total)[0]
                                  for s in (0, 1)]) for g in gammas])
        t_ctrl, t_phys = threshold_of(gammas, ctrl), threshold_of(gammas, phys)
        rows.append((label, t_ctrl, t_phys))
        print(f"  {label:20s} control={t_ctrl:.3f}  physical={t_phys:.3f}")
    moved_down = rows[1][1] < rows[0][1] and rows[1][2] < rows[0][2]
    ctrl_ok = rows[1][1] <= 1.10
    print(f"\nT6c thresholds fall with longer runtime: {moved_down}")
    print(f"T6c control threshold <= 1.10 at T=4000: {ctrl_ok} ({rows[1][1]:.3f})")
    print(f"T6c -> {'PASS (finite-time artifact confirmed)' if (moved_down and ctrl_ok) else 'FAIL (threshold is real; P1 reopens)'}")
    return moved_down, ctrl_ok


if __name__ == "__main__":
    floor_law_test()
    convergence_test()
