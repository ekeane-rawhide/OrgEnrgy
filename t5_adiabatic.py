"""
Step 2: adiabatic tracking test.

Full coupled system:
    dx_i/dt   = beta * (x_i^gamma / sum_j x_j^gamma - x_i)
    dgamma/dt = kappa * (gamma_target - gamma)

gamma_target is stepped 0.7 -> 1.3 at t=0 (distributed -> monopoly bias).
Measure N_eff(t) = 1/sum(x_i^2) relaxation and compare its 10-90% rise time
to the naive first-order-lag estimate 2.2/kappa.
"""
import numpy as np

def run(kappa, beta=1.0, N=20, dt=None, T=None, g_lo=0.7, g_hi=1.3, seed=0):
    rng = np.random.default_rng(seed)
    dt = dt if dt is not None else min(0.01, 0.05 / kappa)
    dt = min(dt, 0.02)
    T = T if T is not None else max(50.0, 30.0 / kappa)
    steps = int(T / dt)

    # start at the gamma=g_lo equilibrium (approx: run gamma fixed a while)
    x = np.ones(N) / N + 1e-3 * rng.normal(size=N)
    x = np.clip(x, 1e-9, None); x /= x.sum()
    gamma = g_lo
    for _ in range(3000):
        xg = x ** gamma
        x = x + dt * beta * (xg / xg.sum() - x)
        x = np.clip(x, 1e-9, None); x /= x.sum()

    # now step gamma_target and integrate the coupled system
    gamma_target = g_hi
    ts, neffs, gs = [], [], []
    t = 0.0
    for i in range(steps):
        xg = x ** gamma
        dx = beta * (xg / xg.sum() - x)
        dg = kappa * (gamma_target - gamma)
        x = x + dt * dx
        gamma = gamma + dt * dg
        x = np.clip(x, 1e-9, None); x /= x.sum()
        t += dt
        if i % max(1, steps // 2000) == 0:
            ts.append(t)
            neffs.append(1.0 / np.sum(x ** 2))
            gs.append(gamma)

    return np.array(ts), np.array(neffs), np.array(gs)


def rise_time(ts, neffs):
    n0, n1 = neffs[0], neffs[-1]
    lo, hi = n0 + 0.1 * (n1 - n0), n0 + 0.9 * (n1 - n0)
    # monotonic check
    d = np.diff(neffs)
    overshoot = neffs.max() > max(n0, n1) + 1e-6 * abs(n1 - n0) if n1 > n0 else neffs.min() < min(n0, n1) - 1e-6*abs(n1-n0)
    try:
        i_lo = np.argmax(neffs >= lo) if n1 > n0 else np.argmax(neffs <= lo)
        i_hi = np.argmax(neffs >= hi) if n1 > n0 else np.argmax(neffs <= hi)
        rt = ts[i_hi] - ts[i_lo]
    except Exception:
        rt = np.nan
    return rt, overshoot


if __name__ == "__main__":
    beta = 1.0
    print(f"{'kappa':>10} {'predicted_rt':>14} {'measured_rt':>14} {'ratio':>8} {'overshoot':>10}")
    for kappa in [beta/50, beta/10, beta/3]:
        ts, neffs, gs = run(kappa, beta=beta)
        rt, overshoot = rise_time(ts, neffs)
        predicted = 2.2 / kappa
        ratio = rt / predicted
        print(f"{kappa:10.4f} {predicted:14.3f} {rt:14.3f} {ratio:8.3f} {str(overshoot):>10}")
