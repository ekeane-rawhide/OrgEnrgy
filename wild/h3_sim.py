"""
H3 sim: rented-memory machine vs exact-count LFU at matched budget,
on a drifting Zipf stream. Also runs the honest self-test (C2): does the
rented score equal the closed-form EMA of access flow?
"""
import numpy as np

K = 200          # item universe
N = 32           # working-set budget (top-N)
STEPS = 12000
DRIFT_EVERY = 2000
ALPHA, BETA = 1.0, 0.01
ZIPF_S = 1.1


def zipf_probs(K, s, perm):
    p = 1.0 / np.arange(1, K + 1) ** s
    p /= p.sum()
    out = np.empty(K)
    out[perm] = p
    return out


def run(seed=0):
    rng = np.random.default_rng(seed)
    perm = rng.permutation(K)
    probs = zipf_probs(K, ZIPF_S, perm)

    rented = np.zeros(K)                 # decaying scores
    lfu = np.zeros(K)                    # exact counts, never decay
    access_log = []                      # for the C2 closed-form check

    hits_rented, hits_lfu = [], []
    for t in range(STEPS):
        if t > 0 and t % DRIFT_EVERY == 0:
            perm = rng.permutation(K)
            probs = zipf_probs(K, ZIPF_S, perm)

        item = rng.choice(K, p=probs)

        # predict BEFORE observing: is the next item in the top-N?
        top_rented = np.argpartition(rented, -N)[-N:]
        top_lfu = np.argpartition(lfu, -N)[-N:]
        hits_rented.append(item in top_rented)
        hits_lfu.append(item in top_lfu)

        # update
        rented *= (1.0 - BETA)
        rented[item] += ALPHA
        lfu[item] += 1
        access_log.append(item)

    return (np.array(hits_rented), np.array(hits_lfu),
            rented, access_log)


def c2_closed_form_check(rented_final, access_log):
    """C_i(T) =? alpha * sum_s (1-beta)^(T-1-s) [i accessed at s],
    with decay applied before each deposit (matching the update order)."""
    T = len(access_log)
    closed = np.zeros(K)
    for s, item in enumerate(access_log):
        closed[item] += ALPHA * (1.0 - BETA) ** (T - 1 - s)
    return np.max(np.abs(closed - rented_final))


if __name__ == "__main__":
    hr_all, hl_all = [], []
    for seed in range(5):
        hr, hl, rented_final, log = run(seed)
        hr_all.append(hr); hl_all.append(hl)
    hr = np.mean(hr_all, axis=0)
    hl = np.mean(hl_all, axis=0)

    def rate(h, a, b):
        return 100 * h[a:b].mean()

    print(f"{'window':>22} {'rented':>8} {'LFU':>8}")
    print(f"{'pre-drift (0-2k)':>22} {rate(hr,0,2000):7.1f}% {rate(hl,0,2000):7.1f}%")
    print(f"{'after 1st drift (2-4k)':>22} {rate(hr,2000,4000):7.1f}% {rate(hl,2000,4000):7.1f}%")
    print(f"{'steady drift (4-12k)':>22} {rate(hr,4000,12000):7.1f}% {rate(hl,4000,12000):7.1f}%")
    gap = rate(hr, 2000, 4000) - rate(hl, 2000, 4000)
    print(f"\nC1 hit-rate gap after first drift: {gap:+.1f} points "
          f"({'PASS (>=5)' if gap >= 5 else 'FAIL'})")

    err = c2_closed_form_check(rented_final, log)
    print(f"C2 closed-form EMA check: max|C - EMA closed form| = {err:.2e} "
          f"({'CONFIRMED: substrate IS an EMA of access flow' if err < 1e-8 else 'deviation found'})")
