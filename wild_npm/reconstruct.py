"""
Reconstruct per-category allocation time series from qualifying dependents.

Rule (pre-registered before looking at any output): if a package's
`dependencies` in a given version names more than one category competitor
simultaneously (e.g. mid-migration, or a wrapper that lists both), its
one dependency slot is split as a fractional allocation across all named
competitors for that version, rather than picking one by an arbitrary
name-order rule. A package with a single named competitor contributes a
full unit to that competitor.

For each qualifying package we take, per PUBLISHED VERSION (deduped by
date via the full doc's top-level "time" map), the set of competitors
present in `dependencies`. This gives one (date, package, {competitor:
fractional_weight}) record per version. Sorting by date within a package
gives its individual switch history; summing across packages at a given
date (last-known-state carried forward) gives the category's aggregate
allocation curve C_i(t).
"""
import json
import sys
from crawl import abbrev_doc, version_times
from categories import CATEGORIES

def dated_choice_series(pkg, competitors):
    """Dependency choice per version comes from the already-cached
    abbreviated doc; publish date per version comes from the separate,
    much smaller `time`-only fetch. Combining the two avoids ever
    caching a full raw doc."""
    doc = abbrev_doc(pkg)
    if not doc or "versions" not in doc:
        return None
    times = version_times(pkg)
    if not times:
        return None
    series = []
    for vstr, vmeta in doc["versions"].items():
        if vstr not in times:
            continue
        deps = vmeta.get("dependencies", {}) or {}
        chosen = [c for c in competitors if c in deps]
        if not chosen:
            continue
        series.append((times[vstr], chosen))
    series.sort(key=lambda x: x[0])
    return series

def build_category(category):
    competitors = CATEGORIES[category]
    qualifying = json.load(open(f"qualifying_{category}.json"))
    qualifying.pop("_scanned", None)
    out = {}
    for i, pkg in enumerate(qualifying):
        s = dated_choice_series(pkg, competitors)
        if s:
            out[pkg] = s
        if i % 25 == 0:
            print(f"  [{category}] dated {i}/{len(qualifying)}", file=sys.stderr)
    json.dump(out, open(f"series_{category}.json", "w"), indent=1)
    return out

if __name__ == "__main__":
    cat = sys.argv[1] if len(sys.argv) > 1 else "http_client"
    build_category(cat)
