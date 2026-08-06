"""
PRE-REGISTERED (written before any series_*.json has been analyzed):

The model claims a routing kernel p_i = C_i^gamma / sum_j C_j^gamma, i.e.
log(p_i/p_j) = gamma * log(C_i/C_j) -- a POWER LAW relating allocation
share to standing count. The competing null the falsify skill demands is
an EXPONENTIAL kernel, p_i ~ exp(gamma * C_i), i.e. log(p_i/p_j) = gamma *
(C_i - C_j). Both are fit by simple linear regression once transformed;
neither gets to be the strawman since both are given the same fitting
freedom (one free slope parameter, no intercept beyond what the
transform allows).

Unit of analysis: at each observed date in a category (a version
publication that changes some package's chosen competitor), we have a
snapshot of C_i(t) = cumulative number of currently-qualifying packages
whose *latest known version as of t* depends on competitor i (last-value-
carried-forward). p_i(t) = C_i(t) / sum_j C_j(t) is that day's share.
Comparing shares one step apart within a category gives (p_i, p_j, C_i,
C_j) tuples usable for both fits.

PREDICTION: the power-law transform (log p_i/p_j vs log C_i/C_j) achieves
higher R^2 than the exponential transform (log p_i/p_j vs C_i - C_j) in a
majority of the 10 categories.

KILL CONDITION: if the power law does not win a majority of categories,
or if R^2 for the winning form is itself low (<0.3) in most categories
--meaning neither kernel actually describes the allocation process --
report that as the finding. Category counts are pre-registered at 10;
no category is dropped post hoc for a bad fit.
"""
import json
import math
import sys
from collections import defaultdict
from categories import CATEGORIES

def load_series(cat):
    try:
        return json.load(open(f"series_{cat}.json"))
    except FileNotFoundError:
        return None

def build_allocation_trajectory(series, competitors):
    """series: {pkg: [(date_iso, [chosen_competitors]), ...]}
    Returns sorted list of (date, {competitor: count}) with last-value-
    carried-forward per package, fractionally splitting a package's slot
    across competitors if multiple are named simultaneously."""
    events = []  # (date, pkg, chosen_list)
    for pkg, s in series.items():
        for date, chosen in s:
            events.append((date, pkg, chosen))
    events.sort(key=lambda x: x[0])

    current = {}  # pkg -> chosen_list (most recent)
    counts = defaultdict(float)
    traj = []
    for date, pkg, chosen in events:
        if pkg in current:
            prev = current[pkg]
            w = 1.0 / len(prev)
            for c in prev:
                counts[c] -= w
        current[pkg] = chosen
        w = 1.0 / len(chosen)
        for c in chosen:
            counts[c] += w
        snapshot = {c: counts[c] for c in competitors if counts[c] > 1e-9}
        traj.append((date, dict(snapshot)))
    return traj

def pairwise_points(traj, min_count=1.0):
    """Yield (log(Ci/Cj), log(pi/pj), Ci-Cj, log-ratio) tuples across all
    snapshots and all competitor pairs present with count >= min_count."""
    pts = []
    for date, snap in traj:
        total = sum(snap.values())
        if total <= 0:
            continue
        items = [(k, v) for k, v in snap.items() if v >= min_count]
        for i in range(len(items)):
            for j in range(len(items)):
                if i == j:
                    continue
                ci, cj = items[i][1], items[j][1]
                pi, pj = ci / total, cj / total
                if pi <= 0 or pj <= 0:
                    continue
                pts.append((math.log(ci / cj), math.log(pi / pj), ci - cj))
    return pts

def linreg_r2(xs, ys):
    n = len(xs)
    if n < 5:
        return None, None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0:
        return None, None
    slope = sxy / sxx
    intercept = my - slope * mx
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - my) ** 2 for y in ys)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else None
    return slope, r2

def fit_category(cat, min_count=1.0):
    series = load_series(cat)
    if not series:
        return None
    traj = build_allocation_trajectory(series, CATEGORIES[cat])
    pts = pairwise_points(traj, min_count=min_count)
    if len(pts) < 20:
        return {"cat": cat, "n_snapshots": len(traj), "n_pairs": len(pts), "insufficient": True}
    log_ratio_C = [p[0] for p in pts]
    log_ratio_p = [p[1] for p in pts]
    diff_C = [p[2] for p in pts]

    gamma_pl, r2_pl = linreg_r2(log_ratio_C, log_ratio_p)
    gamma_exp, r2_exp = linreg_r2(diff_C, log_ratio_p)

    return {
        "cat": cat,
        "n_packages": len(series),
        "n_snapshots": len(traj),
        "n_pairs": len(pts),
        "power_law": {"gamma": gamma_pl, "r2": r2_pl},
        "exponential": {"gamma": gamma_exp, "r2": r2_exp},
        "winner": "power_law" if (r2_pl or -1) > (r2_exp or -1) else "exponential",
    }

if __name__ == "__main__":
    min_count = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
    results = {}
    for cat in CATEGORIES:
        r = fit_category(cat, min_count=min_count)
        results[cat] = r
        print(json.dumps(r))
    json.dump(results, open(f"kernel_fit_min{min_count}.json", "w"), indent=1)
