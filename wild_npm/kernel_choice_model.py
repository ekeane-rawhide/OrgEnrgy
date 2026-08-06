"""
REDESIGN after the first kernel test was caught vacuous: regressing
log(p_i/p_j) on log(C_i/C_j) is an algebraic identity (p_i := C_i/total
=> p_i/p_j = C_i/C_j exactly, for ANY data) -- it produced R^2=1.0,
gamma=1.0 in all 10 categories, the textbook signature (falsify skill
sec 4) of testing a definition instead of a mechanism.

The model's actual claim is about FLOW: when a dependent package makes a
choice (first adoption or a switch), the probability it picks competitor
i depends on the STANDING COUNT C_i at that moment: P(i) = C_i^gamma /
sum_j C_j^gamma (power law) vs P(i) = exp(gamma*C_i)/sum_j exp(gamma*C_j)
(exponential). This is a genuine discrete-choice (conditional logit)
model, fit by maximizing the likelihood of the OBSERVED SEQUENCE OF
CHOICES given the PRE-CHOICE state -- there is no algebraic identity
that forces agreement here; a bad gamma will genuinely score worse than
a good one, and both kernels can lose to the uniform (no-preference)
baseline.

PRE-REGISTERED BEFORE RUNNING:

  Choice set at time t for a category = competitors whose npm package
  already existed (first published version <= t). Multi-choice events
  (a package's dependencies name >1 competitor at once) are EXCLUDED
  from the primary fit (ambiguous single-choice likelihood) -- swept as
  an alternate treatment (include, crediting all named competitors
  equally) to check the verdict doesn't hinge on this choice.

  gamma fit by 1-D maximization of mean log-likelihood over a grid
  refined by golden-section search, separately for power-law and
  exponential forms. Trivial control: gamma=0 uniform choice among the
  available competitors, which both kernels degenerate to at gamma=0 --
  this is the strawman-proof baseline (RESULTS.md sec 5): if fitted
  gamma's likelihood does not beat gamma=0's, there is no signal to
  report.

  PREDICTION: in a majority of the 10 categories, the best-fit kernel
  (power law or exponential, whichever wins) achieves McFadden pseudo-R^2
  = 1 - LL_model/LL_uniform > 0.02 -- i.e., standing count carries some
  detectable information about the next choice, beating pure chance.

  KILL CONDITION: if fewer than half the categories clear pseudo-R^2 >
  0.02, OR if the winning kernel and its fitted gamma are unstable across
  the two multi-choice treatments (exclude vs. split-credit) -- report
  that the preferential-attachment mechanism is not detectable in this
  data, or not identifiable robustly, respectively. Do not lower the
  threshold post hoc to manufacture a pass.
"""
import json
import math
import sys
from collections import defaultdict
from categories import CATEGORIES
from crawl import version_times

def competitor_first_seen(cat):
    """First publish date per competitor package itself."""
    out = {}
    for c in CATEGORIES[cat]:
        times = version_times(c)
        dates = [d for k, d in times.items() if k not in ("created", "modified")]
        out[c] = min(dates) if dates else None
    return out

def load_choice_events(cat, multi_choice="exclude", decisions_only=True):
    """Returns list of (date, pre_state_dict, outcome) where outcome is
    either a single competitor name (exclude mode) or a list of equally
    weighted competitors (split mode).

    decisions_only=True (the honest default, found necessary in the
    adversarial pass): a package that republishes a new version without
    changing its chosen competitor is NOT a fresh decision -- counting
    it as one inflated the raw event stream ~200x with autocorrelated
    repeats of whichever competitor a package already happened to pick,
    which can manufacture apparent preferential-attachment signal for
    free (large C_i attracts more already-settled packages who keep
    republishing, regardless of any real attachment mechanism). Only
    a package's FIRST recorded choice and genuine SWITCHES (chosen set
    differs from the immediately preceding one for that package) count
    as decision events."""
    series = json.load(open(f"series_{cat}.json"))
    events = []
    for pkg, s in series.items():
        for date, chosen in s:
            events.append((date, pkg, chosen))
    events.sort(key=lambda x: x[0])

    competitors = CATEGORIES[cat]
    current = {}  # pkg -> chosen list
    counts = defaultdict(float)
    out = []
    for date, pkg, chosen in events:
        pre_state = {c: counts[c] for c in competitors}
        is_decision = (pkg not in current) or (set(current[pkg]) != set(chosen))
        if not decisions_only or is_decision:
            if len(chosen) == 1:
                out.append((date, pre_state, [chosen[0]]))
            elif multi_choice == "split":
                out.append((date, pre_state, chosen))
        # else exclude ambiguous multi-choice events from the fit

        if pkg in current:
            prev = current[pkg]
            w = 1.0 / len(prev)
            for c in prev:
                counts[c] -= w
        current[pkg] = chosen
        w = 1.0 / len(chosen)
        for c in chosen:
            counts[c] += w
    return out

def log_prob_power(pre_state, competitors, avail, gamma, eps):
    weights = {c: (max(pre_state[c], 0.0) + eps) ** gamma for c in avail}
    total = sum(weights.values())
    return {c: math.log(weights[c] / total) for c in avail}

def log_prob_exp(pre_state, competitors, avail, gamma):
    # normalize by max for numerical stability (shift-invariant softmax)
    m = max(pre_state[c] for c in avail)
    weights = {c: math.exp(gamma * (pre_state[c] - m)) for c in avail}
    total = sum(weights.values())
    return {c: math.log(weights[c] / total) for c in avail}

def mean_ll(events, kernel, gamma, eps=0.5, first_seen=None):
    total_ll = 0.0
    n = 0
    for date, pre_state, outcome in events:
        avail = [c for c in pre_state if first_seen is None or (first_seen.get(c) and first_seen[c] <= date)]
        if len(avail) < 2:
            continue
        if kernel == "power":
            lp = log_prob_power(pre_state, None, avail, gamma, eps)
        elif kernel == "exp":
            lp = log_prob_exp(pre_state, None, avail, gamma)
        else:
            lp = {c: -math.log(len(avail)) for c in avail}
        w = 1.0 / len(outcome)
        ll = 0.0
        ok = True
        for c in outcome:
            if c not in lp:
                ok = False
                break
            ll += w * lp[c]
        if not ok:
            continue
        total_ll += ll
        n += 1
    return (total_ll / n if n else None), n

def golden_section_max(f, lo, hi, tol=1e-3):
    gr = (math.sqrt(5) - 1) / 2
    a, b = lo, hi
    c = b - gr * (b - a)
    d = a + gr * (b - a)
    fc, fd = f(c), f(d)
    while abs(b - a) > tol:
        if fc > fd:
            b, d, fd = d, c, fc
            c = b - gr * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = a + gr * (b - a)
            fd = f(d)
    best = (a + b) / 2
    return best, f(best)

def fit_category(cat, multi_choice="exclude", eps=0.5):
    events = load_choice_events(cat, multi_choice=multi_choice)
    first_seen = competitor_first_seen(cat)

    def power_obj(g):
        ll, n = mean_ll(events, "power", g, eps=eps, first_seen=first_seen)
        return ll if ll is not None else -1e9

    def exp_obj(g):
        ll, n = mean_ll(events, "exp", g, first_seen=first_seen)
        return ll if ll is not None else -1e9

    gamma_pl, ll_pl = golden_section_max(power_obj, 0.0, 4.0)
    gamma_exp, ll_exp = golden_section_max(exp_obj, -2.0, 2.0)
    ll_uniform, n_events = mean_ll(events, "uniform", 0.0, first_seen=first_seen)

    pr2_pl = 1 - ll_pl / ll_uniform if ll_uniform else None
    pr2_exp = 1 - ll_exp / ll_uniform if ll_uniform else None

    return {
        "cat": cat, "multi_choice": multi_choice, "eps": eps,
        "n_events": n_events,
        "ll_uniform": ll_uniform,
        "power_law": {"gamma": gamma_pl, "ll": ll_pl, "pseudo_r2": pr2_pl},
        "exponential": {"gamma": gamma_exp, "ll": ll_exp, "pseudo_r2": pr2_exp},
        "winner": "power_law" if ll_pl > ll_exp else "exponential",
    }

if __name__ == "__main__":
    multi = sys.argv[1] if len(sys.argv) > 1 else "exclude"
    eps = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    results = {}
    for cat in CATEGORIES:
        r = fit_category(cat, multi_choice=multi, eps=eps)
        results[cat] = r
        print(json.dumps(r))
    json.dump(results, open(f"choice_fit_{multi}_eps{eps}.json", "w"), indent=1)
