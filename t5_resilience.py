"""
Step 3: resilience payoff test.

Routing with L4 uniform-flow floor (structural prerequisite for
recoverability after a channel collapses to ~0 in the monopoly phase):

    p_i = (1-m) * x_i^gamma / sum_j x_j^gamma + m/N
    dx_i/dt = beta * (p_i - x_i)
    dgamma/dt = kappa * (gamma_target - gamma)   [adaptive run only]

Scenario: reach monopoly steady state at gamma=1.4, then fail the dominant
channel (set its x_i ~ 0, renormalize). Adaptive run also steps
gamma_target down to 0.6 for a stress window, then back to 1.4. Fixed
control keeps gamma=1.4 throughout (same failure, no gamma response).
"""
import numpy as np


def relax_to_steady_state(x, gamma, m, beta, dt, steps):
    N = len(x)
    for _ in range(steps):
        xg = x ** gamma
        p = (1 - m) * xg / xg.sum() + m / N
        x = x + dt * beta * (p - x)
        x = np.clip(x, 1e-12, None)
        x /= x.sum()
    return x


def run(adaptive, N=20, beta=1.0, m=0.05, kappa=0.1,
        gamma_base=1.4, gamma_stress=0.6, stress_duration=20.0,
        dt=0.02, T_post=120.0, seed=0):
    rng = np.random.default_rng(seed)
    x = np.ones(N) / N + 1e-3 * rng.normal(size=N)
    x = np.clip(x, 1e-9, None); x /= x.sum()

    # reach monopoly steady state at gamma_base
    x = relax_to_steady_state(x, gamma_base, m, beta, dt, 8000)

    # fail the dominant channel; perturb survivors so the post-failure tie
    # isn't a perfectly symmetric (hence never-breaking) fixed point
    dom = np.argmax(x)
    x[dom] = 1e-6
    x = x * (1 + 1e-3 * rng.normal(size=N))
    x = np.clip(x, 1e-12, None); x /= x.sum()

    gamma = gamma_base
    steps = int(T_post / dt)
    ts, neffs, gs = [], [], []
    t = 0.0
    for i in range(steps):
        if adaptive:
            gamma_target = gamma_stress if t < stress_duration else gamma_base
            gamma = gamma + dt * kappa * (gamma_target - gamma)
        xg = x ** gamma
        p = (1 - m) * xg / xg.sum() + m / N
        x = x + dt * beta * (p - x)
        x = np.clip(x, 1e-12, None); x /= x.sum()
        t += dt
        if i % max(1, steps // 3000) == 0:
            ts.append(t)
            neffs.append(1.0 / np.sum(x ** 2))
            gs.append(gamma)

    return np.array(ts), np.array(neffs), np.array(gs)


def time_to_danger(ts, neffs, danger=5.0):
    idx = np.argmax(neffs < danger)
    return ts[idx] if neffs[idx] < danger else np.inf


def auc(ts, neffs, tmax=60.0):
    mask = ts <= tmax
    return np.trapezoid(neffs[mask], ts[mask])


if __name__ == "__main__":
    # NOTE on metric history: the first version of this test used "minimum
    # N_eff over the whole post-failure trajectory" as the resilience
    # metric. That is wrong -- both adaptive and fixed-gamma eventually
    # re-concentrate to the SAME monopoly fixed point once gamma returns to
    # baseline, so "eventual minimum" just measures how far each run got
    # by T_post, not any real difference. The metrics below instead ask
    # how long the redistributed (post-failure) state holds before
    # re-concentration -- that's the actual resilience-relevant question.
    danger = 5.0
    print(f"{'':>24} {'adaptive':>12} {'fixed(1.4)':>12}")
    ratios = []
    for seed in range(6):
        ts_a, neffs_a, gs_a = run(adaptive=True, seed=seed)
        ts_f, neffs_f, gs_f = run(adaptive=False, seed=seed)
        ta = time_to_danger(ts_a, neffs_a, danger)
        tf = time_to_danger(ts_f, neffs_f, danger)
        ratios.append(ta / tf)
        print(f"seed={seed}  time to N_eff<{danger}: {ta:12.2f} {tf:12.2f}   ratio={ta/tf:.2f}")

    ts_a, neffs_a, gs_a = run(adaptive=True, seed=0)
    ts_f, neffs_f, gs_f = run(adaptive=False, seed=0)
    auc_a, auc_f = auc(ts_a, neffs_a), auc(ts_f, neffs_f)
    i20a = np.argmax(ts_a >= 20); i20f = np.argmax(ts_f >= 20)

    print(f"\nAUC(N_eff, t=0..60):      adaptive={auc_a:8.1f}  fixed={auc_f:8.1f}  "
          f"({100*(auc_a-auc_f)/auc_f:+.1f}%)")
    print(f"N_eff at t=20 (end of stress window): adaptive={neffs_a[i20a]:.2f}  fixed={neffs_f[i20f]:.2f}")
    print(f"mean time-to-danger ratio across seeds: {np.mean(ratios):.2f}x")
    print(f"kill condition (need >= 1.10x): {'PASS' if np.mean(ratios) >= 1.10 else 'FAIL'}")
