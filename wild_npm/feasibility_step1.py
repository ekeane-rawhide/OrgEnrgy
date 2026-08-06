"""
Step 1 feasibility crawl — ONE category (HTTP clients) before scaling.

PRE-REGISTERED (written before this script produced any output):

  Category: npm HTTP client libraries.
  Competitor set (chosen from public knowledge, not from crawl output):
    axios, node-fetch, got, superagent, request, cross-fetch, ky, undici,
    isomorphic-fetch, needle

  Candidate dependent pool: built from ~20 generic search-term queries
  UNRELATED to "http" or "fetch" (cli, react, webpack, server, sdk,
  framework, build, test, utils, app, typescript, vue, graphql, docker,
  auth, database, logger, config, cron, parser), size=250 each, deduped.
  This is a broad, category-agnostic popularity sample, not cherry-picked
  HTTP consumers -- picking search terms FROM the category would bias the
  sample toward exactly the answer we're testing for.

  PREDICTION: at least 15 packages in this broad sample will show, in
  their abbreviated registry doc, a `dependencies` entry naming one of
  the 10 competitor libraries in at least one published version. That
  would be enough to attempt a real switch-history reconstruction.

  KILL CONDITION: fewer than 15 qualifying packages found, OR the
  qualifying packages' version histories show no actual switching
  (single pinned choice for 100% of their history, zero transitions) --
  either means individual-package reconstruction cannot produce a time
  series and the whole crawl-based design (not just this category) is
  infeasible with the reachable APIs. Report that plainly; do not widen
  the candidate pool post hoc to rescue the number.
"""
import json
import sys
from crawl import search_raw, abbrev_doc, full_doc

CATEGORY = "http_client"
COMPETITORS = [
    "axios", "node-fetch", "got", "superagent", "request",
    "cross-fetch", "ky", "undici", "isomorphic-fetch", "needle",
]

GENERIC_TERMS = [
    "cli", "react", "webpack", "server", "sdk", "framework", "build",
    "test", "utils", "app", "typescript", "vue", "graphql", "docker",
    "auth", "database", "logger", "config", "cron", "parser",
]

def build_candidate_pool():
    names = set()
    for term in GENERIC_TERMS:
        obj = search_raw(term, size=250)
        for o in obj.get("objects", []):
            n = o.get("package", {}).get("name")
            if n:
                names.add(n)
        print(f"  term={term!r} cumulative pool={len(names)}", file=sys.stderr)
    return sorted(names)

def package_ever_depends_on_competitor(pkg):
    doc = abbrev_doc(pkg)
    if not doc or "versions" not in doc:
        return None
    hits = {}
    for vstr, vmeta in doc["versions"].items():
        deps = vmeta.get("dependencies", {}) or {}
        chosen = [c for c in COMPETITORS if c in deps]
        if chosen:
            hits[vstr] = chosen
    return hits if hits else None

def main():
    pool = build_candidate_pool()
    print(f"Candidate pool size (pre-filter, deduped): {len(pool)}")
    json.dump(pool, open("candidate_pool.json", "w"), indent=1)

    qual_path = "qualifying_http_client.json"
    qualifying = json.load(open(qual_path)) if __import__("os").path.exists(qual_path) else {}
    scanned = set(qualifying.get("_scanned", []))
    qualifying.pop("_scanned", None)

    for i, pkg in enumerate(pool):
        if pkg in COMPETITORS or pkg in scanned:
            continue  # exclude the competitors themselves from the dependent pool
        hits = package_ever_depends_on_competitor(pkg)
        if hits:
            qualifying[pkg] = hits
        scanned.add(pkg)
        if i % 50 == 0:
            print(f"  scanned {i}/{len(pool)}, qualifying so far={len(qualifying)}", file=sys.stderr)
            qualifying["_scanned"] = sorted(scanned)
            json.dump(qualifying, open(qual_path, "w"), indent=1)
            qualifying.pop("_scanned", None)

    qualifying["_scanned"] = sorted(scanned)
    json.dump(qualifying, open(qual_path, "w"), indent=1)
    qualifying.pop("_scanned", None)
    print(f"\nQualifying dependents found: {len(qualifying)}")
    for pkg, hits in list(qualifying.items())[:30]:
        print(f"  {pkg}: {hits}")

    # switching check: does any qualifying package show >1 distinct
    # competitor choice across its version history?
    switchers = {p: h for p, h in qualifying.items()
                 if len({c for chosen in h.values() for c in chosen}) > 1}
    print(f"\nPackages whose dependency choice varies across versions: {len(switchers)}")
    for pkg, hits in list(switchers.items())[:15]:
        print(f"  {pkg}: {hits}")

    print("\n--- PRE-REGISTERED VERDICT ---")
    if len(qualifying) < 15:
        print(f"KILL: only {len(qualifying)} qualifying dependents (<15). "
              "Crawl-based reconstruction infeasible at this sample size.")
    else:
        print(f"PASS threshold: {len(qualifying)} >= 15 qualifying dependents.")
    if len(switchers) == 0:
        print("KILL: zero packages show any switching behavior across versions. "
              "No flow to observe -- allocations are static pins, not a dynamical system.")
    else:
        print(f"PASS: {len(switchers)} packages show switching behavior.")

if __name__ == "__main__":
    main()
