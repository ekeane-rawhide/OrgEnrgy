"""
T4/T6: microgrid domain test -- the first test of the deposition/decay
model against a system with physics in it.

N storage cells share one DC bus. A controller allocates incoming charge
current by the power-law rule C_i^gamma / sum_j C_j^gamma. But allocated
current is NOT accepted current: each cell tapers its acceptance as it
fills (constant-voltage charging), refused current is redistributed to
cells with headroom, and cells discharge into a load.

The routing weights are fed by ACCEPTED current, so physical saturation
feeds back onto the structural dynamics -- a coupling the abstract model
(dC/dt = alpha*F*C^gamma/sum C^gamma - beta*C) does not contain.

Question under test: does the gamma=1 threshold survive that feedback?
"""
import numpy as np

N = 20
ALPHA, BETA = 1.0, 0.05
F = 1.0
CAP = 1.0          # cell capacity
LAM = 1.0          # load draw rate (per unit stored charge)
I_CAP = 0.5        # acceptance-taper scale; I_max(SOC) = I_CAP*(1-SOC)
DT = 0.02
T = 1000.0


def allocate(C, gamma, soc, i_cap, rounds=8):
    """Allocate F by the power-law rule, then apply per-cell acceptance
    limits and redistribute refused current to cells with headroom
    (weight-proportionally). Returns accepted current per cell."""
    w = np.clip(C, 1e-12, None) ** gamma
    p = w / w.sum()

    if not np.isfinite(i_cap):
        return F * p                      # taper disabled (control)

    headroom = np.clip(i_cap * (1.0 - soc), 0.0, None)
    accepted = np.zeros(N)
    remaining = F
    active = headroom > 1e-12

    for _ in range(rounds):
        if remaining <= 1e-12 or not active.any():
            break
        share = np.where(active, p, 0.0)
        s = share.sum()
        if s <= 1e-12:
            break
        offer = remaining * share / s
        take = np.minimum(offer, headroom - accepted)
        take = np.clip(take, 0.0, None)
        accepted += take
        remaining -= take.sum()
        active = (headroom - accepted) > 1e-12

    return accepted


def run(gamma, i_cap=I_CAP, seed=0, t_total=T, dt=DT):
    rng = np.random.default_rng(seed)
    C = np.ones(N) / N * (1.0 + 1e-3 * rng.normal(size=N))
    C = np.clip(C, 1e-9, None)
    soc = np.zeros(N)

    steps = int(t_total / dt)
    for _ in range(steps):
        accepted = allocate(C, gamma, soc, i_cap)
        C = C + dt * (ALPHA * accepted - BETA * C)
        soc = soc + dt * (accepted - LAM * soc) / CAP
        C = np.clip(C, 1e-12, None)
        soc = np.clip(soc, 0.0, 1.0)

    x = C / C.sum()
    return 1.0 / np.sum(x ** 2), soc, C


def sweep(gammas, i_cap, seeds=(0, 1, 2)):
    out = []
    for g in gammas:
        vals = [run(g, i_cap=i_cap, seed=s)[0] for s in seeds]
        out.append(np.mean(vals))
    return np.array(out)


def threshold_of(gammas, neffs):
    """gamma at which N_eff crosses the midpoint of its own range."""
    hi, lo = neffs.max(), neffs.min()
    mid = 0.5 * (hi + lo)
    for i in range(len(neffs) - 1):
        a, b = neffs[i], neffs[i + 1]
        if (a - mid) * (b - mid) <= 0 and a != b:
            f = (a - mid) / (a - b)
            return gammas[i] + f * (gammas[i + 1] - gammas[i])
    return np.nan


if __name__ == "__main__":
    gammas = np.round(np.arange(0.6, 1.65, 0.1), 2)

    print("P3 CONTROL: taper disabled (pure abstract model, must give ~1.0)")
    neff_ctrl = sweep(gammas, i_cap=np.inf)
    for g, n in zip(gammas, neff_ctrl):
        print(f"  gamma={g:4.2f}  N_eff={n:6.2f}  N_eff/N={n/N:5.3f}")
    thr_ctrl = threshold_of(gammas, neff_ctrl)
    print(f"  control threshold = {thr_ctrl:.3f}")

    print("\nP1/P2 REAL TEST: taper on (physical saturation feedback)")
    neff_phys = sweep(gammas, i_cap=I_CAP)
    for g, n in zip(gammas, neff_phys):
        print(f"  gamma={g:4.2f}  N_eff={n:6.2f}  N_eff/N={n/N:5.3f}")
    thr_phys = threshold_of(gammas, neff_phys)
    print(f"  physical threshold = {thr_phys:.3f}")

    floor = neff_phys.min()
    print(f"\nP1 threshold in [0.9, 1.1]: {thr_phys:.3f} -> "
          f"{'PASS' if 0.9 <= thr_phys <= 1.1 else 'FAIL'}")
    print(f"P2 depth floor N_eff={floor:.2f} > 1 (no true monopoly): "
          f"{'PASS' if floor > 1.0 else 'FAIL'}  "
          f"[monopoly floor would be N_eff=1.00]")
    print(f"P3 control threshold in [0.9, 1.1]: {thr_ctrl:.3f} -> "
          f"{'PASS' if 0.9 <= thr_ctrl <= 1.1 else 'FAIL'}")
