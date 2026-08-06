"""
T7: estimate gamma from observed trajectory data alone.

Given only C_i(t) -- no knowledge of alpha, beta, F, or the kernel:

  1. S = sum_i C_i obeys dS/dt = alpha*F - beta*S for ANY kernel, so
     regressing dS/dt on S gives beta (= -slope) and alpha*F (= intercept).
  2. dC_i/dt = alpha*F*p_i - beta*C_i inverts to the realised share
     p_i = (dC_i/dt + beta*C_i)/(alpha*F).
  3. log p_i = gamma*log C_i + c(t), with c(t) shared across channels at
     time t. Centering per time point removes c(t); gamma is the pooled
     slope through the origin.

Kernel identification is threshold-free: fit both candidate kernels
(power law: log p ~ log C; exponential: log p ~ C) and report which
explains more variance. No hand-picked R^2 bar.

Pre-registered in LEDGER.md (section T7) before this file existed.
"""
import numpy as np

ALPHA, F_DRIVE, BETA_TRUE = 1.0, 1.0, 0.1
WEIGHTED = True   # T7b repair #1: compositional (share-magnitude) weighting
USE_INTEGRAL = True  # T7c repair #2: integral form, no differentiation


def generate(gamma, N=25, T=60.0, dt=0.01, sample_every=20, kernel="power",
             temp=None, noise=0.0, seed=0):
    """Simulate the true dynamics and return sampled (times, C[t, i])."""
    rng = np.random.default_rng(seed)
    C = rng.uniform(0.3, 1.7, size=N)          # spread => regressor variance
    times, traj = [], []
    steps = int(T / dt)
    for s in range(steps):
        if kernel == "power":
            w = np.clip(C, 1e-12, None) ** gamma
        else:                                   # L6 exponential/softmax
            w = np.exp(C / temp)
        p = w / w.sum()
        C = C + dt * (ALPHA * F_DRIVE * p - BETA_TRUE * C)
        C = np.clip(C, 1e-12, None)
        if s % sample_every == 0:
            times.append(s * dt)
            traj.append(C.copy())
    times, traj = np.array(times), np.array(traj)
    if noise > 0:
        traj = traj * (1.0 + noise * rng.normal(size=traj.shape))
        traj = np.clip(traj, 1e-12, None)
    return times, traj


def _r2(x, y, w=None):
    """Weighted R^2 of a through-origin fit y = m x (data pre-centered).

    Routing shares are compositional data whose log-residual variance
    scales roughly as 1/p, so w=p is the quasi-likelihood weighting for
    share data -- derived from the data type, not from the answer."""
    if w is None:
        w = np.ones_like(x)
    denom = np.sum(w * x * x)
    if denom < 1e-30:
        return np.nan, np.nan
    m = np.sum(w * x * y) / denom
    resid = y - m * x
    ss_tot = np.sum(w * y * y)
    if ss_tot < 1e-30:
        return m, np.nan
    return m, 1.0 - np.sum(w * resid ** 2) / ss_tot


def estimate(times, traj, channels=None):
    """Return dict with gamma_hat, beta_hat, and both kernels' R^2."""
    S = traj.sum(axis=1)          # all channels -- conservation requires it
    if channels is not None:
        traj = traj[:, channels]
    dS = np.gradient(S, times)
    A = np.vstack([S, np.ones_like(S)]).T
    slope, intercept = np.linalg.lstsq(A, dS, rcond=None)[0]
    beta_hat, drive_hat = -slope, intercept
    if drive_hat <= 0:
        return dict(gamma_hat=np.nan, beta_hat=beta_hat,
                    r2_power=np.nan, r2_exp=np.nan, kernel="undetermined")

    dC = np.gradient(traj, times, axis=0)
    p = (dC + beta_hat * traj) / drive_hat

    # centered-per-timepoint regressors kill the time-varying intercept
    xs_pow, xs_exp, ys, ws = [], [], [], []
    for t in range(len(times)):
        good = (p[t] > 1e-12) & (traj[t] > 1e-12)
        if good.sum() < 3:
            continue
        lp = np.log(p[t][good])
        lc = np.log(traj[t][good])
        c = traj[t][good]
        ys.append(lp - lp.mean())
        xs_pow.append(lc - lc.mean())
        xs_exp.append(c - c.mean())
        ws.append(p[t][good])
    if not ys:
        return dict(gamma_hat=np.nan, beta_hat=beta_hat,
                    r2_power=np.nan, r2_exp=np.nan, kernel="undetermined")

    y = np.concatenate(ys)
    w = np.concatenate(ws) if WEIGHTED else None
    gamma_hat, r2_power = _r2(np.concatenate(xs_pow), y, w)
    _, r2_exp = _r2(np.concatenate(xs_exp), y, w)
    kernel = "power" if (np.nan_to_num(r2_power, nan=-9) >
                         np.nan_to_num(r2_exp, nan=-9)) else "exponential"
    return dict(gamma_hat=gamma_hat, beta_hat=beta_hat,
                r2_power=r2_power, r2_exp=r2_exp, kernel=kernel)


def estimate_integral(times, traj, channels=None, block=6):
    """T7c repair #2: INTEGRAL form -- never differentiate noisy data.

    Finite differencing is the known noise amplifier here (np.gradient on
    5%-noise data). Integrating the ODE over intervals instead is the
    standard treatment for ODE parameter estimation from noisy series:

        C_i(b) - C_i(a) = alpha*F * int_a^b p_i dt - beta * int_a^b C_i dt

    Aggregate: S(b)-S(a) = alpha*F*(b-a) - beta*int S dt, a 2-parameter
    linear solve for (alpha*F, beta) with no derivatives at all.
    """
    # S MUST sum over ALL channels: the aggregate identity
    # dS/dt = alphaF - beta*S relies on sum_i p_i = 1, true only for the
    # whole system. Subsetting before summing violates conservation and
    # corrupts beta_hat/drive_hat. (Bug found in adversarial review.)
    S_full = traj.sum(axis=1)
    if channels is not None:
        traj = traj[:, channels]
    n = len(times)
    edges = [(i, min(i + block, n - 1)) for i in range(0, n - 1, block)]
    edges = [(a, b) for a, b in edges if b > a]
    if len(edges) < 3:
        return dict(gamma_hat=np.nan, beta_hat=np.nan,
                    r2_power=np.nan, r2_exp=np.nan, kernel="undetermined")

    S = S_full
    rows, rhs = [], []
    for a, b in edges:
        dt_ = times[b] - times[a]
        int_S = np.trapezoid(S[a:b + 1], times[a:b + 1])
        rows.append([dt_, -int_S])
        rhs.append(S[b] - S[a])
    (drive_hat, beta_hat) = np.linalg.lstsq(np.array(rows), np.array(rhs),
                                            rcond=None)[0]
    if drive_hat <= 0:
        return dict(gamma_hat=np.nan, beta_hat=beta_hat,
                    r2_power=np.nan, r2_exp=np.nan, kernel="undetermined")

    xs_pow, xs_exp, ys, ws = [], [], [], []
    for a, b in edges:
        dt_ = times[b] - times[a]
        int_C = np.trapezoid(traj[a:b + 1], times[a:b + 1], axis=0)
        pbar = (traj[b] - traj[a] + beta_hat * int_C) / (drive_hat * dt_)
        cbar = int_C / dt_
        good = (pbar > 1e-12) & (cbar > 1e-12)
        if good.sum() < 3:
            continue
        lp, lc = np.log(pbar[good]), np.log(cbar[good])
        ys.append(lp - lp.mean())
        xs_pow.append(lc - lc.mean())
        xs_exp.append(cbar[good] - cbar[good].mean())
        ws.append(pbar[good])
    if not ys:
        return dict(gamma_hat=np.nan, beta_hat=beta_hat,
                    r2_power=np.nan, r2_exp=np.nan, kernel="undetermined")

    y = np.concatenate(ys)
    w = np.concatenate(ws) if WEIGHTED else None
    gamma_hat, r2_power = _r2(np.concatenate(xs_pow), y, w)
    _, r2_exp = _r2(np.concatenate(xs_exp), y, w)
    kernel = "power" if (np.nan_to_num(r2_power, nan=-9) >
                         np.nan_to_num(r2_exp, nan=-9)) else "exponential"
    return dict(gamma_hat=gamma_hat, beta_hat=beta_hat,
                r2_power=r2_power, r2_exp=r2_exp, kernel=kernel)


def stability_spread(gamma, noise=0.0, seed=0):
    """P4: spread of gamma_hat across analyst choices that should not
    matter -- sampling interval, transient window, channel subset."""
    ests = []
    for sample_every in (10, 20, 40):
        times, traj = generate(gamma, sample_every=sample_every,
                               noise=noise, seed=seed)
        n = len(times)
        for lo, hi in ((0, n), (0, n // 2), (n // 4, n)):
            for chans in (None, np.arange(0, 25, 2)):
                r = ESTIMATOR(times[lo:hi], traj[lo:hi], channels=chans)
                if np.isfinite(r["gamma_hat"]):
                    ests.append(r["gamma_hat"])
    ests = np.array(ests)
    return ests.max() - ests.min(), ests.mean(), len(ests)


ESTIMATOR = None  # bound below

if __name__ == "__main__":
    import sys
    ESTIMATOR = estimate_integral if USE_INTEGRAL else estimate
    globals()['estimate'] = ESTIMATOR
    gammas = [0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8]

    print("P1  recovery from noiseless data (tolerance +-0.10)")
    print(f"{'true':>6} {'est':>8} {'err':>8} {'R2_pow':>8} {'R2_exp':>8} {'kernel':>12}")
    p1_worst = 0.0
    for g in gammas:
        t, tr = generate(g)
        r = estimate(t, tr)
        err = abs(r["gamma_hat"] - g)
        p1_worst = max(p1_worst, err)
        print(f"{g:6.2f} {r['gamma_hat']:8.3f} {err:8.3f} {r['r2_power']:8.4f} "
              f"{r['r2_exp']:8.4f} {r['kernel']:>12}")
    print(f"P1 worst error {p1_worst:.3f} -> {'PASS' if p1_worst <= 0.10 else 'FAIL'}\n")

    print("P2  recovery with 5% observation noise (tolerance +-0.20)")
    p2_worst = 0.0
    for g in gammas:
        errs = []
        for sd in range(3):
            t, tr = generate(g, noise=0.05, seed=sd)
            errs.append(abs(estimate(t, tr)["gamma_hat"] - g))
        e = float(np.mean(errs))
        p2_worst = max(p2_worst, e)
        print(f"{g:6.2f}  mean abs err {e:6.3f}")
    print(f"P2 worst error {p2_worst:.3f} -> {'PASS' if p2_worst <= 0.20 else 'FAIL'}\n")

    print("P3  misspecification, threshold-free (must identify kernel both ways)")
    t, tr = generate(1.3)
    rp = estimate(t, tr)
    ok_pow = rp["kernel"] == "power"
    print(f"  power-law data      R2_pow={rp['r2_power']:.4f} R2_exp={rp['r2_exp']:.4f}"
          f" -> says {rp['kernel']}  {'ok' if ok_pow else 'WRONG'}")
    t, tr = generate(None, kernel="exp", temp=0.35)
    re_ = estimate(t, tr)
    ok_exp = re_["kernel"] == "exponential"
    print(f"  exponential data    R2_pow={re_['r2_power']:.4f} R2_exp={re_['r2_exp']:.4f}"
          f" -> says {re_['kernel']}  {'ok' if ok_exp else 'WRONG'}")
    print(f"P3 -> {'PASS' if (ok_pow and ok_exp) else 'FAIL'}\n")

    print("P4  stability across analyst choices (spread must be < 0.15)")
    p4_worst = 0.0
    for g in (0.6, 1.0, 1.4):
        spread, mean, n = stability_spread(g)
        p4_worst = max(p4_worst, spread)
        print(f"  true={g:4.2f}  spread={spread:6.3f}  mean={mean:6.3f}  ({n} configs)")
    print(f"P4 worst spread {p4_worst:.3f} -> {'PASS' if p4_worst < 0.15 else 'FAIL'}")
