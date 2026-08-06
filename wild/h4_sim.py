"""
H4 sim: the Individuation Hypothesis.

A structureless medium on a ring. Nothing in the update names, counts,
or indexes a "part":

    du/dt = F*cap[u^gamma / sum u^gamma] - beta*u + D*laplacian(u)

Parts are not modelled -- they are MEASURED, by counting peaks in the
resulting field. Question: does the emergent part-count match L7, a law
derived for a system with a fixed number of parts?

Predictions pre-registered in wild/ROUND2.md before this was run.
"""
import numpy as np

M = 128           # medium resolution (NOT a number of parts)
BETA = 0.05
F = 1.0
LAM = 1.0
GAMMA = 1.6
DT = 0.05
T = 2000.0


def l7_floor(i_cap):
    a = i_cap / (1.0 + i_cap)
    k = int(np.floor(1.0 / a + 1e-9))
    r = 1.0 - k * a
    return 1.0 / (k * a * a + r * r)


def laplacian(u):
    return np.roll(u, 1) + np.roll(u, -1) - 2.0 * u


def allocate(u, gamma, soc, i_cap, rounds=8):
    w = np.clip(u, 1e-12, None) ** gamma
    p = w / w.sum()
    headroom = np.clip(i_cap * (1.0 - soc), 0.0, None)
    accepted = np.zeros(M)
    remaining, active = F, headroom > 1e-12
    for _ in range(rounds):
        if remaining <= 1e-12 or not active.any():
            break
        share = np.where(active, p, 0.0)
        s = share.sum()
        if s <= 1e-12:
            break
        take = np.clip(np.minimum(remaining * share / s, headroom - accepted), 0.0, None)
        accepted += take
        remaining -= take.sum()
        active = (headroom - accepted) > 1e-12
    return accepted


def count_peaks(u):
    """Count local maxima of the field that carry real mass."""
    thresh = u.mean()
    left, right = np.roll(u, 1), np.roll(u, -1)
    is_peak = (u > left) & (u >= right) & (u > thresh)
    return int(is_peak.sum())


def run(i_cap, D, seed=0, gamma=GAMMA, t_total=T):
    rng = np.random.default_rng(seed)
    u = np.ones(M) / M * (1.0 + 1e-2 * rng.normal(size=M))
    u = np.clip(u, 1e-9, None)
    soc = np.zeros(M)
    for _ in range(int(t_total / DT)):
        acc = allocate(u, gamma, soc, i_cap)
        u = u + DT * (acc - BETA * u + D * laplacian(u))
        soc = soc + DT * (acc - LAM * soc)
        u = np.clip(u, 1e-12, None)
        soc = np.clip(soc, 0.0, 1.0)
    x = u / u.sum()
    return count_peaks(u), 1.0 / np.sum(x ** 2), u


if __name__ == "__main__":
    print("C1/C2: does a medium with no predefined parts individuate into L7's count?")
    print(f"{'I_cap':>7} {'L7 pred':>8} {'peaks(seeds)':>16} {'N_eff':>8} {'rel err':>9}  verdict")
    worst = 0.0
    for i_cap in [0.50, 0.25, 0.10]:
        pred = l7_floor(i_cap)
        peaks, neffs = [], []
        for s in (0, 1, 2):
            pk, ne, _ = run(i_cap, D=1e-4, seed=s)
            peaks.append(pk); neffs.append(ne)
        ne_mean = float(np.mean(neffs))
        rel = abs(ne_mean - pred) / pred
        worst = max(worst, rel)
        print(f"{i_cap:7.2f} {pred:8.2f} {str(peaks):>16} {ne_mean:8.2f} {rel:8.1%}  "
              f"{'ok' if rel <= 0.10 and max(peaks)-min(peaks) <= 1 else 'DEVIATES'}")

    print("\nC3: is the count a diffusion artifact? (I_cap=0.25, L7 predicts 5)")
    for D in [1e-5, 1e-4, 1e-3, 1e-2]:
        pk, ne, _ = run(0.25, D=D, seed=0)
        print(f"  D={D:.0e}  peaks={pk:3d}  N_eff={ne:6.2f}")

    print(f"\nC2 worst relative error: {worst:.1%} -> "
          f"{'PASS' if worst <= 0.10 else 'FAIL'}")
