"""
THE test this whole crawl exists to run.

PRE-REGISTERED BEFORE COMPUTING ANY CORRELATION:

  Early window: events with date < (min_date + frac * (max_date -
  min_date)) for that category, frac in {0.3, 0.4, 0.5} (swept, not
  cherry-picked after seeing results). Fit gamma_early via the same
  discrete-choice power-law model already validated (kernel_choice_model,
  exclude-multi-choice, eps=0.5).

  Later concentration: at the LAST observed snapshot in each category's
  trajectory, compute HHI = sum(p_i^2) over normalized shares. HHI=1/K
  is perfectly even (K competitors), HHI=1 is total monopoly.

  PREDICTION (direction stated in advance, matching the model's own
  claim): categories with higher gamma_early should show higher final
  HHI. Spearman rank correlation across the 10 categories, one point per
  category, sign +.

  KILL CONDITION: if the correlation is not positive and is not
  distinguishable from zero (given only 10 categories, this is a weak
  test almost by construction -- report the correlation AND its spread
  across the three window fractions, and say plainly if N=10 cannot
  support a confident verdict either way). A correlation that reverses
  sign across the three pre-registered window fractions is a kill by
  itself: it means the "prediction" is a property of the window choice,
  not of the categories.
"""
import json
import math
from categories import CATEGORIES
from kernel_choice_model import load_choice_events, mean_ll, golden_section_max, competitor_first_seen

def fit_gamma_window(cat, frac, first_seen, min_events=30):
    events = load_choice_events(cat, multi_choice="exclude")
    if not events:
        return None
    dates = [e[0] for e in events]
    dmin, dmax = min(dates), max(dates)
    cutoff = dmin[:4]  # fallback if string compare fails oddly; ISO dates compare lexically fine
    # ISO8601 strings compare correctly lexicographically
    span = dates_to_days(dmax) - dates_to_days(dmin)
    cutoff_day = dates_to_days(dmin) + frac * span
    early = [e for e in events if dates_to_days(e[0]) <= cutoff_day]
    if len(early) < min_events:
        return None

    def obj(g):
        ll, n = mean_ll(early, "power", g, eps=0.5, first_seen=first_seen)
        return ll if ll is not None else -1e9

    gamma, ll = golden_section_max(obj, 0.0, 4.0)
    return {"gamma_early": gamma, "n_early_events": len(early), "cutoff": cutoff_day_to_date(cutoff_day)}

def dates_to_days(iso):
    # crude but monotonic: parse YYYY-MM-DD prefix to ordinal day count
    import datetime
    try:
        d = datetime.date.fromisoformat(iso[:10])
        return (d - datetime.date(2000, 1, 1)).days
    except Exception:
        return 0

def cutoff_day_to_date(day):
    import datetime
    return str(datetime.date(2000, 1, 1) + datetime.timedelta(days=int(day)))

def final_hhi(cat):
    series = json.load(open(f"series_{cat}.json"))
    events = []
    for pkg, s in series.items():
        for date, chosen in s:
            events.append((date, pkg, chosen))
    events.sort(key=lambda x: x[0])
    from collections import defaultdict
    current, counts = {}, defaultdict(float)
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
    total = sum(counts.values())
    if total <= 0:
        return None
    shares = [v / total for v in counts.values() if v > 1e-9]
    hhi = sum(s ** 2 for s in shares)
    return {"hhi": hhi, "n_competitors_active": len(shares), "total_slots": total}

def spearman(xs, ys):
    n = len(xs)
    def rank(vals):
        order = sorted(range(len(vals)), key=lambda i: vals[i])
        ranks = [0] * len(vals)
        for r, i in enumerate(order):
            ranks[i] = r + 1
        return ranks
    rx, ry = rank(xs), rank(ys)
    d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
    return 1 - 6 * d2 / (n * (n ** 2 - 1)) if n > 1 else None

if __name__ == "__main__":
    import sys
    min_events = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    results = {}
    for frac in (0.3, 0.4, 0.5):
        row = {}
        for cat in CATEGORIES:
            first_seen = competitor_first_seen(cat)
            g = fit_gamma_window(cat, frac, first_seen, min_events=min_events)
            h = final_hhi(cat)
            if g and h:
                row[cat] = {**g, **h}
        gammas = [row[c]["gamma_early"] for c in row]
        hhis = [row[c]["hhi"] for c in row]
        rho = spearman(gammas, hhis)
        results[frac] = {"per_category": row, "spearman_rho": rho, "n_categories": len(row)}
        print(f"frac={frac}: n={len(row)} spearman_rho={rho}")
        for c in row:
            print(f"    {c:18} gamma_early={row[c]['gamma_early']:.3f}  hhi={row[c]['hhi']:.3f}  n_active={row[c]['n_competitors_active']}")
    json.dump(results, open("early_gamma_vs_concentration.json", "w"), indent=1)
